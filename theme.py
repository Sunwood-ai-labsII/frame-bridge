import gradio as gr

def create_zen_theme():
    """
    ZENテーマの作成
    和モダンなデザインで、使いやすさと美しさを追求したテーマ
    """
    return gr.Theme(
        primary_hue="amber",
        secondary_hue="stone",
        neutral_hue="slate",
        text_size="md",
        spacing_size="lg",
        radius_size="sm",
        font=[
            "Hiragino Sans",
            "Noto Sans JP",
            "Yu Gothic",
            "system-ui",
            "sans-serif"
        ],
        font_mono=[
            "SF Mono",
            "Monaco",
            "monospace"
        ]
    ).set(
        body_background_fill="#ffffff",
        body_text_color="#3d405b",
        button_primary_background_fill="#d4a574",
        button_primary_background_fill_hover="#c19660",
        button_primary_text_color="#ffffff",
        button_secondary_background_fill="#f5f2ed",
        button_secondary_text_color="#3d405b",
        input_background_fill="#ffffff",
        input_border_color="#d4c4a8",
        input_border_color_focus="#d4a574",
        block_background_fill="#ffffff",
        block_border_color="#e8e2d5",
        block_border_width="3px",
        panel_background_fill="#ffffff",
        panel_border_color="#e8e2d5",
        slider_color="#d4a574",
    )