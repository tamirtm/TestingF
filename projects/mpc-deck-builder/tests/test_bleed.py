from PIL import Image

from mpcdeck.bleed import add_bleed, bleed_px, canvas_px


def test_mpc_template_size():
    # MPC Autofill treats a 1110 px tall image as 300 DPI -> 2.72 x 3.70 in with bleed
    assert canvas_px(300) == (816, 1110)
    assert canvas_px(600) == (1632, 2220)
    assert bleed_px(300) == 36            # 0.12 in ≈ 1/8 in


def test_add_bleed_extends_edges():
    src = Image.new("RGB", (745, 1040), "black")
    src.paste(Image.new("RGB", (745 - 40, 1040 - 40), "white"), (20, 20))
    out = add_bleed(src, 300)
    assert out.size == (816, 1110)
    assert out.getpixel((0, 0)) == (0, 0, 0)            # bleed corner copies the black border
    assert out.getpixel((408, 555)) == (255, 255, 255)  # centre untouched
