import pyautogui as pg


INVENTORY = (110, 210, 600, 740)
VAULT_INVENTORY = (1227, 219, 607, 298)
VAULT_REGION = (525, 213, 927, 867)

VAULT_FOLDER_REGION = (1346, 129, 416, 107)
INVENTORY_FOLDER_REGION = (313, 148, 261, 80)


def filter_points(targets, min_dist) -> set:
    """Filters a set of points by min dist from each other.
    This is important because pyautogui may locate the same template
    multiple times on the same position.
    """
    filtered = set()

    while targets:
        eps = targets.pop()
        for point in targets:
            if all(abs(c2 - c1) < min_dist for c2, c1 in zip(eps, point)):
                break
        else:
            filtered.add(eps)
    return filtered


def to_paint_vault_visible() -> bool:
    """Checks if the `to_paint` vault is visible."""
    return (
        pg.locateOnScreen("assets/to_paint.png", region=VAULT_REGION, confidence=0.8)
        is not None
    )


def painted_vault_visible() -> bool:
    """Checks if the `painted` vault is visible."""
    return (
        pg.locateOnScreen("assets/painted.png", region=VAULT_REGION, confidence=0.8)
        is not None
    )


def get_piece_in_inv(piece) -> tuple:
    """Gets center of an armor piece in the inventory"""
    return pg.locateCenterOnScreen(
        f"assets/{piece}.png", region=INVENTORY, confidence=0.8
    )


def get_piece_in_vault(piece) -> tuple:
    """Gets center of an armor piece in the vault"""
    return pg.locateCenterOnScreen(
        f"assets/{piece}.png", region=VAULT_INVENTORY, confidence=0.8
    )


def vault_is_open() -> bool:
    """Checks if the vault is open"""
    return pg.locateOnScreen(
        "assets/folder_view.png", region=VAULT_FOLDER_REGION, confidence=0.8
    )


def inventory_is_open() -> bool:
    """Checks if the inventory is open"""
    return pg.locateOnScreen(
        "assets/folder_view.png", region=INVENTORY_FOLDER_REGION, confidence=0.8
    )


def get_amount_of_pieces(piece) -> bool:
    """Checks how many pieces of the given piece we currently have"""
    return len(
        filter_points(
            set(
                pg.locateAllOnScreen(
                    f"assets/{piece}.png", region=INVENTORY, confidence=0.8
                )
            ),
            min_dist=20,
        )
    )

def find_random_color():
    """Grabs a random color in the inventory"""
    return pg.locateCenterOnScreen("assets/color.png", region=INVENTORY, confidence=0.8, grayscale=True)

def get_piece_positions(piece) -> list:
    """Returns all positions of an armor piece in the inventory"""
    return [
        (round(box[0] + (0.5 * box[2])), round(box[1] + (0.5 * box[3])))
        for box in filter_points(
            set(
                pg.locateAllOnScreen(
                    f"assets/{piece}.png", region=INVENTORY, confidence=0.8
                )
            ),
            min_dist=20,
        )
    ]
