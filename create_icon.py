from PIL import Image, ImageDraw

# 创建一个 256x256 的图像
size = (256, 256)
img = Image.new('RGBA', size, (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# 绘制一个简单的圆形
circle_color = (99, 102, 241)  # 使用主题色
margin = 20
draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], fill=circle_color)

# 保存为 ICO 文件
img.save('icon.ico', format='ICO') 