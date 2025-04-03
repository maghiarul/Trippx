import flet as ft
from flet import (
    Column,
    Container,
    GestureDetector,
    Icon,
    Image,
    Page,
    Row,
    Stack,
    Text,
    TextButton,
    Icons,
    ProgressBar,
)
from predict_nou import predict_rating

def random_card(page: ft.Page, hotel_data: dict, on_swipe_callback) -> Container:
    # Global state for the card
    is_expanded = False       # Whether details are expanded
    details_container = None  # Will hold the details container widget
    overlay_control = None    # For collapsing details when clicking outside
    hotel_name = hotel_data["Name"]
    overall_rating = hotel_data["Rating"]
    image_url = hotel_data["ImageURL"]
    current_pred_rf, current_pred_xgb = predict_rating(hotel_data)
    current_pred_rf = round(current_pred_rf, 2)
    current_pred_xgb = round(current_pred_xgb, 2)

    # Convert CSV string values to floats where applicable.
    staff = float(hotel_data["Staff"])
    facilities = float(hotel_data["Facilities"])
    cleanliness = float(hotel_data["Cleanliness"])
    comfort = float(hotel_data["Comfort"])
    value_for_money = float(hotel_data["Value_for_money"])
    location_val = float(hotel_data["Location"])
    wifi = float(hotel_data["Wifi"])

    # Normalization helper (assuming ratings out of 10)
    norm = lambda x: x / 10.0

    # --------------------------------
    # Details Container Creator
    # --------------------------------
    def create_details_container(expanded: bool) -> Container:
        # Define all 7 rating containers:
        ratings = [
            Container(
                content=Column(
                    controls=[
                        Text("Staff", size=12, width=80),
                        Row(
                            controls=[
                                ProgressBar(value=norm(staff), width=150, color="#0066CC"),
                                Text(f"{staff:.1f}", size=12),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=-3,
                ),
            ),
            Container(
                content=Column(
                    controls=[
                        Text("Facilities", size=12, width=80),
                        Row(
                            controls=[
                                ProgressBar(value=norm(facilities), width=150, color="#0066CC"),
                                Text(f"{facilities:.1f}", size=12),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=-3,
                ),
            ),
            Container(
                content=Column(
                    controls=[
                        Text("Cleanliness", size=12, width=80),
                        Row(
                            controls=[
                                ProgressBar(value=norm(cleanliness), width=150, color="#0066CC"),
                                Text(f"{cleanliness:.1f}", size=12),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=-3,
                ),
            ),
            Container(
                content=Column(
                    controls=[
                        Text("Comfort", size=12, width=80),
                        Row(
                            controls=[
                                ProgressBar(value=norm(comfort), width=150, color="#0066CC"),
                                Text(f"{comfort:.1f}", size=12),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=-3,
                ),
            ),
            # Extra ratings:
            Container(
                content=Column(
                    controls=[
                        Text("Value", size=12, width=80),
                        Row(
                            controls=[
                                ProgressBar(value=norm(value_for_money), width=150, color="#0066CC"),
                                Text(f"{value_for_money:.1f}", size=12),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=-3,
                ),
            ),
            Container(
                content=Column(
                    controls=[
                        Text("Location", size=12, width=80),
                        Row(
                            controls=[
                                ProgressBar(value=norm(location_val), width=150, color="#0066CC"),
                                Text(f"{location_val:.1f}", size=12),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=-3,
                ),
            ),
            Container(
                content=Column(
                    controls=[
                        Text("Wifi", size=12, width=80),
                        Row(
                            controls=[
                                ProgressBar(value=norm(wifi), width=150, color="#0066CC"),
                                Text(f"{wifi:.1f}", size=12),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ],
                    spacing=-3,
                ),
            ),
        ]
        if not expanded:
            # Collapsed state: use only the first 4 rating containers.
            ratings_collapsed = ratings[:4]
            ratings_column = Column(controls=ratings_collapsed, spacing=10)
            details_left = Column(
                controls=[
                    Text(hotel_name, weight="bold", size=16, color="white"),
                    Row(
                        controls=[
                            Text(overall_rating, size=14, color="white", weight="bold"),
                            Icon(Icons.STAR, size=16, color="gold"),
                        ],
                        spacing=2,
                    ),
                    TextButton(
                        "Read More",
                        on_click=lambda e: expand_details(e),
                        style=ft.ButtonStyle(color="#0066CC"),
                    ),
                ],
                spacing=5,
            )
            details_row = Row(
                controls=[
                    Container(content=details_left, width=250),
                    Container(content=ratings_column, padding=ft.padding.only(left=20)),
                ],
                spacing=10,
            )
            return Container(
                content=details_row,
                padding=15,
                bgcolor="#1F1F1F",
                border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                top=550,
                height=200,
                width=500,
            )
        else:
            # Expanded state: All 7 ratings are used.
            ratings_column = Column(controls=ratings, spacing=10)
            details_left = Column(
                controls=[
                    Text(hotel_name, weight="bold", size=16, color="white"),
                    Row(
                        controls=[
                            Text(overall_rating, size=14, color="white", weight="bold"),
                            Icon(Icons.STAR, size=16, color="gold"),
                        ],
                        spacing=2,
                    ),
                    TextButton(
                        "Read Less",
                        on_click=lambda e: collapse_details(e),
                        style=ft.ButtonStyle(color="#0066CC"),
                    ),
                ],
                spacing=5,
            )
            details_row = Row(
                controls=[
                    Container(content=details_left, width=250),
                    Container(content=ratings_column, padding=ft.padding.only(left=20)),
                ],
                spacing=10,
            )
            return Container(
                content=details_row,
                padding=15,
                bgcolor="#1F1F1F",
                border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                top=400,
                height=350,
                width=500,
            )
    
    def expand_details(e):
        nonlocal is_expanded, details_container, overlay_control, swipe_offset
        if not is_expanded:
            is_expanded = True
            new_details = create_details_container(True)
            details_container.content = new_details.content
            details_container.top = new_details.top
            details_container.height = new_details.height
            details_container.update()
            swipe_offset = 0  # disable swiping when expanded
            overlay_control = Container(
                left=0,
                top=0,
                width=page.window.width,
                height=page.window.height,
                bgcolor="transparent",
                on_click=lambda e: collapse_details(e),
            )
            page.overlay.append(overlay_control)
            page.update()
    
    def collapse_details(e):
        nonlocal is_expanded, details_container, overlay_control
        if is_expanded:
            is_expanded = False
            new_details = create_details_container(False)
            details_container.content = new_details.content
            details_container.top = new_details.top
            details_container.height = new_details.height
            details_container.update()
            page.overlay.clear()
            page.update()
    
    # --------------------------------
    # Complete Hotel Card Creation
    # --------------------------------
    def create_hotel_card_full() -> ft.Stack:
        nonlocal details_container
        rating_badge = Row(
            controls=[
                Container(
                    content=Row(
                        controls=[
                            ft.Image(src="E:/@py_proj/tripper/tripx/src/assets/icons/rdf.svg", width=16, height=16, tooltip="Random Forest", color="#1F1F1F"),
                            ft.Text(current_pred_rf, weight="bold", color="#1F1F1F"),
                        ],
                        spacing=5,  # Adjust spacing for readability
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor="#FFB703",  # Yellow color for Random Forest badge
                    border_radius=10,
                    padding=5,
                    width=100,  # Increased width to fit all elements
                ),
                Container(
                    content=Row(
                        controls=[
                            ft.Image(src="E:/@py_proj/tripper/tripx/src/assets/icons/xgboost.svg", width=16, height=16, tooltip="XGBoost", color="white"),
                            ft.Text(current_pred_xgb, weight="bold", color="white"),
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor="#2C5282",  # Blue color for XGBoost badge
                    border_radius=10,
                    padding=5,
                    width=100,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        )
        maps_button = Container(
            content=Icon(Icons.MAP, color="white"),
            bgcolor="#4285F4",
            width=40,
            height=40,
            border_radius=ft.border_radius.all(20),
            alignment=ft.alignment.center,
            on_click=lambda e: page.launch_url("https://www.google.com/maps/search/?api=1&query=" + hotel_name.replace(" ", "+")),
        )
        hotel_image = Image(
            src=(image_url if image_url else "https://via.placeholder.com/500"),
            fit="cover",
            height=550,
            width=500,
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
        )
        details_container = create_details_container(False)
        return ft.Stack(
            controls=[
                Container(content=hotel_image, width=500, height=550),
                Container(content=rating_badge, left=10, top=10),
                Container(content=maps_button, right=10, top=500),
                details_container,
            ]
        )
    
    card = create_hotel_card_full()
    
    # --------------------------------
    # Swipe Gesture & Smooth Animation Setup
    # --------------------------------
    swipe_offset = 0
    
    def pan_update(e: ft.DragUpdateEvent):
        nonlocal swipe_offset
        if is_expanded:
            return  # Disable swiping when details are expanded.
        swipe_offset += e.delta_x
        pos_container.left = swipe_offset
        pos_container.top = -swipe_offset/20 if swipe_offset > 0 else abs(swipe_offset)/20
        pos_container.opacity = max(0, 1 - abs(swipe_offset)/300)
        if pos_container.page:  # Ensure it's added to the page before updating
            pos_container.update()
    
    def pan_end(e: ft.DragEndEvent):
        nonlocal swipe_offset
        if is_expanded:
            return
        threshold = 300
        if abs(swipe_offset) >= threshold:
            direction = "right" if swipe_offset > 0 else "left"

        # Notify `main.py` about swipe action
        if direction and on_swipe_callback:
            on_swipe_callback(hotel_data, direction, current_pred_rf, current_pred_xgb)
        swipe_offset = 0
        pos_container.animate_duration = 300
        pos_container.animate_curve = "easeInOut"
        pos_container.left = 0
        pos_container.top = 0
        pos_container.opacity = 1
        if pos_container.page:  # Ensure it's added to the page before updating
            pos_container.update()
    
    gesture_detector = ft.GestureDetector(
        content=card,
        on_pan_update=pan_update,
        on_pan_end=pan_end,
    )
    
    pos_container = ft.Container(
        content=gesture_detector,
        left=0,
        width=500,
        height=750,  # 550 (image) + details (200 collapsed or 350 expanded)
        opacity=1,
    )
    
    gesture_stack = ft.Stack(
        width=500,
        height=750,
        alignment=ft.alignment.center,
        controls=[pos_container],
    )
    
    return gesture_stack, current_pred_rf, current_pred_xgb
