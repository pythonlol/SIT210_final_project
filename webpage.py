import plotly.graph_objects as go
import numpy as np
import time
import smbus
bus=smbus.SMBus(1)

x = list(range(0, 20))
data = []
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=data, mode="lines+markers", text=data, textposition="top center", textfont={"color": "black", "size": 12}))
fig.update_xaxes(range=[0, 19], dtick=1)
fig.update_yaxes(range=[0, 100])

fig.update_layout(
    title={
        "text": "soil moisture level",
        "font": {
            "color": "black",
            "size": 24
        },
        "x": 0.5 
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
        if len(data) < 20:
            data.append(tr)
        else:
            data.pop(0)
            data.append(tr)
        frame = go.Frame(data=[go.Scatter(x=x, y=data, text=data, mode="lines+markers+text")])
        frames.append(frame)

    fig.frames = frames
    fig.show()

if __name__ == '__main__':
    main()
