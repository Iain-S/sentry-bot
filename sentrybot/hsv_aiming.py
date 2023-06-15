# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments
# pylint: disable=no-member

"""Au."""

import logging
import math
from typing import Any, List, Optional, Tuple

import cv2  # type: ignore
import numpy

from sentrybot.settings import Settings
from sentrybot.turret_controller import TurretController


def _add_text(frame: numpy.ndarray, text: str, colour: Tuple = (0, 0, 255)) -> None:
    cv2.putText(
        frame,
        text,
        (10, 600),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        colour,
        1,
        cv2.LINE_AA,
    )


def _draw_point(
    frame: numpy.ndarray,
    x_coordinate: float,
    y_coordinate: float,
    radius: int = 8,
    colour: Tuple = (255, 0, 0),
    thickness: int = 2,
) -> None:
    cv2.circle(frame, (int(x_coordinate), int(y_coordinate)), radius, colour, thickness)


def _aim(
    target_center_x: float,
    target_center_y: float,
    camera_center_x: float,
    camera_center_y: float,
    image_width: float,
    image_height: float,
    firing_threshold: int,
    streaming_frame: numpy.ndarray,
    turret_controller: Optional[TurretController],
) -> bool:
    red_colour: Tuple = (0, 0, 255)
    _draw_point(streaming_frame, target_center_x, target_center_y, colour=red_colour)

    camera_offset: int = Settings().camera_offset
    turret_center_x: float = camera_center_x
    turret_center_y: float = camera_center_y + camera_offset
    green_colour: Tuple = (0, 255, 0)
    _draw_point(streaming_frame, turret_center_x, turret_center_y, colour=green_colour)

    logging.warning(
        "image_width %s image_height: %s", str(image_width), str(image_height)
    )
    logging.warning(
        "image_center_x: %s image_center_y: %s",
        str(camera_center_x),
        str(camera_center_y),
    )
    logging.warning(
        "current_center_x: %s current_center_y: %s",
        str(target_center_x),
        str(target_center_y),
    )

    current_distance: float = math.dist(
        (turret_center_x, turret_center_y), (target_center_x, target_center_y)
    )
    x_distance: float = abs(turret_center_x - target_center_x)
    y_distance: float = abs(turret_center_y - target_center_y)

    logging.warning(
        "current_distance: %s firing_threshold: %s x_distance: %s y_distance: %s",
        str(current_distance),
        str(firing_threshold),
        str(x_distance),
        str(y_distance),
    )

    default_nudge: float = Settings().default_nudge
    if current_distance <= firing_threshold:
        _add_text(streaming_frame, "FIRE!!!!", colour=red_colour)
        if turret_controller:
            turret_controller.launch()

        return True
    if target_center_x < turret_center_x and x_distance > firing_threshold:
        _add_text(streaming_frame, f"Object left. Distance: {int(current_distance)}")
        if turret_controller:
            turret_controller.nudge_x(default_nudge)
    elif target_center_x > turret_center_x and x_distance > firing_threshold:
        _add_text(streaming_frame, f"Object right Distance: {int(current_distance)}")
        if turret_controller:
            turret_controller.nudge_x(-default_nudge)
    elif target_center_y < turret_center_y and y_distance > firing_threshold:
        _add_text(streaming_frame, f"Object up Distance: {int(current_distance)}")
        if turret_controller:
            turret_controller.nudge_y(default_nudge)
    elif target_center_y > turret_center_y and y_distance > firing_threshold:
        _add_text(streaming_frame, f"Object Down Distance: {int(current_distance)}")
        if turret_controller:
            turret_controller.nudge_y(-default_nudge)
    else:
        _add_text(
            streaming_frame, f"NO ACTION TAKEN! Distance: {int(current_distance)}"
        )

    return False


def _detect_target(
    contours: List, minimum_target_area: float, maximum_target_area: float
) -> Optional[Any]:
    current_max_area: float = 0
    current_contour = None

    for contour in contours:
        # _, _, width, height = _contour_to_rectangle(contour)
        # area = width * height

        area = cv2.contourArea(contour)

        if area > current_max_area:
            current_max_area = area
            current_contour = contour
    if minimum_target_area < current_max_area < maximum_target_area:
        return current_contour

    return None


def _contour_to_rectangle(contour: Any) -> Tuple[int, int, int, int]:
    polygonal_curve = cv2.approxPolyDP(contour, 3, True)
    bounding_rectangle = cv2.boundingRect(polygonal_curve)

    return (
        bounding_rectangle[0],
        bounding_rectangle[1],
        bounding_rectangle[2],
        bounding_rectangle[3],
    )


def _draw_contour(frame: numpy.ndarray, contour: Any) -> None:
    (
        contour_x,
        contour_y,
        contour_width,
        contour_height,
    ) = _contour_to_rectangle(contour)

    cv2.rectangle(
        frame,
        pt1=(contour_x, contour_y),
        pt2=(contour_x + contour_width, contour_y + contour_height),
        color=(255, 0, 0),
        thickness=3,
    )
    cv2.drawContours(frame, [contour], 0, (0, 255, 0), 3)


def do_mask_based_aiming(
    frame: numpy.ndarray,
    turret_controller: Optional[TurretController],
    minimum_hue: int = 30,
    maximum_hue: int = 50,
    minimum_value: int = 0,
    maximum_value: int = 255,
    minimum_saturation: int = 100,
    maximum_saturation: int = 255,
    minimum_target_area: int = 0,
    maximum_target_area: int = 100000,
) -> Tuple[numpy.ndarray, bool]:
    """Aim with a HSV mask."""
    image_height, image_width, _ = frame.shape
    image_center_x: float = image_width / 2
    image_center_y: float = image_height / 2

    hsv_frame: numpy.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_bound: numpy.ndarray = numpy.array(
        [minimum_hue, minimum_saturation, minimum_value]
    )
    upper_bound: numpy.ndarray = numpy.array(
        [
            maximum_hue,
            maximum_saturation,
            maximum_value,
        ]  # Take a look at this. The original code had a bug here.
    )

    colour_mask: numpy.ndarray = cv2.inRange(hsv_frame, lower_bound, upper_bound)

    streaming_frame = frame
    if Settings().streaming_source == 1:
        streaming_frame = hsv_frame
    elif Settings().streaming_source == 2:
        streaming_frame = colour_mask

    _draw_point(streaming_frame, image_center_x, image_center_y)

    projectile_launched: bool = False
    contours, _ = cv2.findContours(colour_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    logging.warning("Detected contours: %s", str(len(contours)))

    contour_target = _detect_target(contours, minimum_target_area, maximum_target_area)

    if contour_target is None:
        _add_text(streaming_frame, "No target detected")
    else:
        # _draw_contour(streaming_frame, contour_target)

        position_x, position_y, width, height = _contour_to_rectangle(contour_target)
        # current_max_area: float = width * height
        current_center_x: float = position_x + width / 2
        current_center_y: float = position_y + height / 2

        firing_threshold: int = Settings().firing_threshold

        projectile_launched = _aim(
            current_center_x,
            current_center_y,
            image_center_x,
            image_center_y,
            image_width,
            image_height,
            firing_threshold,
            streaming_frame,
            turret_controller,
        )

    # e.g. turret_controller.nudge_x()

    return streaming_frame, projectile_launched
