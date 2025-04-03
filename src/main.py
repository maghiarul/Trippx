import flet as ft
from flet import (
    Column,
    Container,
    ElevatedButton,
    Icon,
    Image,
    ProgressBar,
    Page,
    Row,
    SearchBar,
    Text,
    TextButton,
    Icons,
    Stack,
    CrossAxisAlignment,
    GestureDetector,
    TextStyle,
)

def main(page: Page):
    page.title = "Hotel Booking App"
    page.padding = 0
    page.bgcolor = "#B3DAFF"  # Light blue background
    page.window.height = 1080
    page.window.width = 800

    # --------------------------------
    # Search Bar Setup
    # --------------------------------
    search = SearchBar(
        width=350,
        bar_hint_text="Where you want to go . . .",
        bar_leading=Image(src="icons/search.svg", width=16, height=16, tooltip="Search", color="#1F1F1F"),
        bar_padding=ft.padding.only(left=20),
        bar_bgcolor="white",
        bar_hint_text_style=TextStyle(color="#1F1F1F"),
        bar_text_style=TextStyle(color="#1F1F1F"),
    )

    # --------------------------------
    # Hotel Card Creation Function (with Ratings)
    # --------------------------------
    def create_hotel_card():
        # Rating Badge (overlaid on the hotel image)
        rating_badge = Container(
            content=Row(
                [
                    Text("9.1", weight="bold", color="#1F1F1F"),
                    Image(src="icons/sparkles.svg", width=16, height=16, tooltip="Deep Search", color="#1f1f1f"),
                ],
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor="#FFB703",
            border_radius=10,
            padding=5,
            width=60,
        )

        # Hotel Image
        hotel_image = Image(
            src=(
                "https://cf.bstatic.com/xdata/images/hotel/max1024x768/"
                "645831931.jpg?k=662168ae499aabe3cbb542923db1466e418727d04f0632f490786ad0c8f550d0&o="
            ),
            fit="cover",
            height=550,
            width=500,
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
        )

        # Ratings Column (for individual aspects)
        ratings_column = Column(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            Text("Staff", size=12, width=80),
                            Row(
                                controls=[
                                    ProgressBar(value=0.88, width=150, color="#0066CC"),
                                    Text("8.8", size=12),
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
                                    ProgressBar(value=0.83, width=150, color="#0066CC"),
                                    Text("8.3", size=12),
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
                                    ProgressBar(value=0.86, width=150, color="#0066CC"),
                                    Text("8.6", size=12),
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
                                    ProgressBar(value=0.95, width=150, color="#0066CC"),
                                    Text("9.5", size=12),
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.START,
                            ),
                        ],
                        spacing=-3,
                    ),
                ),
            ],
            spacing=10,
        )

        # Left Text Details Column
        details_left = Column(
            controls=[
                Text("DeGoya Studios Bucharest Old Town", weight="bold", size=16, color="white"),
                Row(
                    controls=[
                        Text("8.5", size=14, color="white", weight="bold"),
                        Image(src="icons/star.svg", width=16, height=16, tooltip="Deep Search", color="#FFB703"),

                    ],
                    spacing=2,
                ),
                Text(
                    "DeGoya Studios Bucharest Old Town is located in Bucharest, just a 14-minute drive...",
                    size=12,
                    color="white",
                ),
                TextButton("Read More", style=ft.ButtonStyle(color="#0066CC")),
            ],
            spacing=5,
        )

        # Compose Details Row with left text area and right ratings.
        details_row = Row(
            controls=[
                Container(content=details_left, width=250),
                Container(content=ratings_column, padding=ft.padding.only(left=20))
            ],
            spacing=10,
        )

        # Hotel Details Section Container
        hotel_details = Container(
            content=details_row,
            padding=15,
            bgcolor="#1F1F1F",
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
        )

        # Assemble the full hotel card using a Stack:
        # • The hotel image at the top,
        # • The rating badge overlaid on the image,
        # • The details section positioned below the image.
        card_stack = Stack(
            controls=[
                Container(content=hotel_image, width=500, height=550),
                Container(content=rating_badge, left=10, top=10),
                Container(content=hotel_details, width=500, height=200, top=550),
            ]
        )
        return card_stack

    # Create the hotel card.
    card = create_hotel_card()

    # --------------------------------
    # Swipe Gesture Setup
    # --------------------------------
    # We wrap the card in a GestureDetector and place it in an absolutely positioned container
    # named "pos_container" so that we may update its "left" property on drag events.
    swipe_offset = 0  # Cumulative horizontal drag offset

    def pan_update(e: ft.DragUpdateEvent):
        nonlocal swipe_offset
        swipe_offset += e.delta_x
        pos_container.left = swipe_offset
        pos_container.update()

    def pan_end(e: ft.DragEndEvent):
        nonlocal swipe_offset
        threshold = 300  # Threshold (in pixels) for a swipe action.
        if abs(swipe_offset) >= threshold:
            if swipe_offset > 0:
                print("Swiped Right")
            else:
                print("Swiped Left")
        # Reset the position to center
        swipe_offset = 0
        pos_container.left = 0
        pos_container.update()

    # Wrap the card in a GestureDetector.
    gesture_detector = GestureDetector(
        content=card,
        on_pan_update=pan_update,
        on_pan_end=pan_end,
    )

    # The container "pos_container" is a direct child of a Stack so that we can update its "left" property.
    pos_container = Container(
        content=gesture_detector,
        left=0,
        width=500,
        height=750,  # Sum of image (550) + details (200) heights
    )

    # Place "pos_container" in a Stack with fixed dimensions.
    gesture_stack = Stack(
        width=500,
        height=750,
        alignment=ft.alignment.center,
        controls=[pos_container],
    )

    # --------------------------------
    # Bottom Buttons & Location Info
    # --------------------------------
    location_column = Column(
        controls=[
            Text("Current Location", size=12, color="#1F1F1F"),
            Text("Bucuresti", size=20, weight="bold", color="#1F1F1F"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=-3,
    )

    search_buttons = Row(
        controls=[
            ElevatedButton(
                content=Row(
                    controls=[
                        Image(src="icons/brain-circuit.svg", width=16, height=16, tooltip="Machine Learning", color="#A3CEF1"),
                        Text("Machine Learning", weight="bold", color="#A3CEF1"),
                    ],
                    spacing=5,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                style=ft.ButtonStyle(
                    bgcolor="#2C5282",
                    color="white",
                    padding=15,
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
            ),
            ElevatedButton(
                content=Row(
                    controls=[
                        Image(src="icons/brain-cog.svg", width=16, height=16, tooltip="Deep Search", color="#A3CEF1"),
                        Text("Deep Search", weight="bold", color="#A3CEF1"),
                    ],
                    spacing=5,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                style=ft.ButtonStyle(
                    bgcolor="#4299E1",
                    color="white",
                    padding=15,
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
            ),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    main_column = Column(
        controls=[
            Container(content=search, margin=ft.margin.only(top=10, bottom=10), alignment=ft.alignment.center),
            Container(content=location_column, alignment=ft.alignment.center),
            Container(content=gesture_stack, alignment=ft.alignment.center, margin=ft.margin.only(top=10, bottom=10)),
            Container(content=search_buttons, alignment=ft.alignment.center, margin=ft.margin.only(bottom=10)),
        ]
    )

    page.add(Container(content=main_column, padding=10))

ft.app(target=main, assets_dir="assets")
