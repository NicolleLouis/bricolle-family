import base64


class FigureToImage:
    @staticmethod
    def generate_chart_image(fig):
        img_bytes = fig.to_image(format="png")
        return base64.b64encode(img_bytes).decode('utf-8')
