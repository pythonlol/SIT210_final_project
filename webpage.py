import plotly.graph_objects as go
import numpy as np
import time
import smbus
bus=smbus.SMBus(1)
# 创建两个列表作为数据源
x = list(range(0, 20))
data = []
# 创建一个Figure对象
fig = go.Figure()
# 添加一条折线图
fig.add_trace(go.Scatter(x=x, y=data, mode="lines+markers", text=data, textposition="top center", textfont={"color": "black", "size": 12}))
# 设置x轴和y轴的范围
fig.update_xaxes(range=[0, 19], dtick=1)
fig.update_yaxes(range=[0, 100])
# 设置动画参数
fig.update_layout(
    title={
        "text": "soil moisture level",
        "font": {
            "color": "black",
            "size": 24
        },
        "x": 0.5 # 居中显示
    },
    updatemenus=[
        dict(
            type="buttons",
            buttons=[dict(label="Play", method="animate", args=[None, {"frame": {"duration": 0}}])],
        )
    ],
    yaxis=dict(range=[0, 100], autorange=False),
)

def main():
    global data
    #time.sleep(1)
    frames = []
    for i in range(100):
        bus.write_byte(0x48,0x43)
        tr=bus.read_byte(0x48)
        tr = np.interp(tr, [0, 255], [0, 100])
        # 如果data列表的长度小于20，就在末尾添加一个随机数
        if len(data) < 20:
            data.append(tr)
        # 如果data列表的长度等于20，就将第一个元素弹出，并在末尾添加一个随机数
        else:
            data.pop(0)
            data.append(tr)
        # 创建一个帧对象，更新折线图的数据
        frame = go.Frame(data=[go.Scatter(x=x, y=data, text=data, mode="lines+markers+text")])
        frames.append(frame)
    # 将帧对象添加到图表中
    fig.frames = frames
    # 显示图表
    fig.show()

if __name__ == '__main__':
    main()
