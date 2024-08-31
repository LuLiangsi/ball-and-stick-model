import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor
import pyqtgraph as pg

class AnimatedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        
        self.setGeometry(100, 100, 900, 600)
        self.setWindowTitle('杆球模拟')

        # 设置窗口大小
        self.setFixedSize(900, 600)

        # 设置动画参数
        self.center_x = 250
        self.center_y = 350
        self.theta = 0.0
        self.theta_dot = 0.0
        self.g = 9.8
        self.mu = 0.0
        self.L_animation = 150
        self.L_real = 0.15

        # 设置定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)

        self.begin_button = QPushButton('开始', self)
        self.begin_button.clicked.connect(self.toggle_animation)

        # # 初始值设置布局
        self.init_layout = QVBoxLayout()
        self.init_layout.addWidget(self.begin_button)

        lable_text_width = 70
        lable_value_width = 70

        theta_set_layout = QHBoxLayout()
        theta_lable = QLabel('初始角度:')
        theta_lable.setFixedWidth(lable_text_width)
        theta_value_label = QLabel('0°')
        theta_value_label.setFixedWidth(lable_value_width)
        theta_slider = QSlider(Qt.Horizontal, self)
        theta_slider.setFixedWidth(150)
        theta_slider.setRange(-180, 180)
        theta_slider.setValue(0)
        theta_slider.valueChanged.connect(lambda value, lbl=theta_value_label: lbl.setText(f'{value}°'))
        theta_set_layout.addWidget(theta_lable)
        theta_set_layout.addWidget(theta_value_label)
        theta_set_layout.addWidget(theta_slider)
        
        theta_dot_set_layout = QHBoxLayout()
        theta_dot_lable = QLabel('初始角速度:')
        theta_dot_lable.setFixedWidth(lable_text_width)
        theta_dot_value_lable = QLabel('0 rad/s')
        theta_dot_value_lable.setFixedWidth(lable_value_width)
        theta_dot_slider = QSlider(Qt.Horizontal, self)
        theta_dot_slider.setFixedWidth(150)
        theta_dot_slider.setRange(-1800, 1800)
        theta_dot_slider.setValue(0)
        theta_dot_slider.valueChanged.connect(lambda value, lbl=theta_dot_value_lable: lbl.setText(f'{value} rad/s'))
        theta_dot_set_layout.addWidget(theta_dot_lable)
        theta_dot_set_layout.addWidget(theta_dot_value_lable)
        theta_dot_set_layout.addWidget(theta_dot_slider)

        gravity_set_layout = QHBoxLayout()
        gravity_lable = QLabel('重力加速度:')
        gravity_lable.setFixedWidth(lable_text_width)
        gravity_value_label = QLabel('9.8 m/s^2')
        gravity_value_label.setFixedWidth(lable_value_width)
        gravity_slider = QSlider(Qt.Horizontal, self)
        gravity_slider.setFixedWidth(150)
        gravity_slider.setRange(0, 200)
        gravity_slider.setValue(98)
        gravity_slider.valueChanged.connect(lambda value, lbl=gravity_value_label: lbl.setText(f'{value/10} m/s^2'))
        gravity_set_layout.addWidget(gravity_lable)
        gravity_set_layout.addWidget(gravity_value_label)
        gravity_set_layout.addWidget(gravity_slider)

        mu_set_layout = QHBoxLayout()
        mu_lable = QLabel('摩擦系数:')
        mu_lable.setFixedWidth(lable_text_width)
        mu_value_label = QLabel('0.5')
        mu_value_label.setFixedWidth(lable_value_width)
        mu_slider = QSlider(Qt.Horizontal, self)
        mu_slider.setFixedWidth(150)
        mu_slider.setRange(0, 1000)
        mu_slider.setValue(500)
        mu_slider.valueChanged.connect(lambda value, lbl=mu_value_label: lbl.setText(f'{value/1000}'))
        mu_set_layout.addWidget(mu_lable)
        mu_set_layout.addWidget(mu_value_label)
        mu_set_layout.addWidget(mu_slider)

        L_set_layout = QHBoxLayout()
        L_lable = QLabel('杆长:')
        L_lable.setFixedWidth(lable_text_width)
        L_value_label = QLabel('1.5 m')
        L_value_label.setFixedWidth(lable_value_width)
        L_slider = QSlider(Qt.Horizontal, self)
        L_slider.setFixedWidth(150)
        L_slider.setRange(1, 100)
        L_slider.setValue(15)
        L_slider.valueChanged.connect(lambda value, lbl=L_value_label: lbl.setText(f'{value/10} m'))
        L_set_layout.addWidget(L_lable)
        L_set_layout.addWidget(L_value_label)
        L_set_layout.addWidget(L_slider)

        # 创造选择
        self.combo = QComboBox(self)
        self.combo.addItem('角度-时间')
        self.combo.addItem('角速度-时间')
        self.combo.addItem('角速度-角度')
        self.combo.currentIndexChanged.connect(self.function_plot_chose)


        # 创建绘图区域
        self.function_plot = pg.PlotWidget()
        self.function_plot.showGrid(x=True, y=True)
        self.function_plot.setFixedSize(400, 300)


        # 初始化绘图数据
        self.function_plot_data = self.function_plot.plot([0], [0])


        self.sliders = [theta_slider, theta_dot_slider, gravity_slider, mu_slider, L_slider]

        self.init_layout.addLayout(theta_set_layout)
        self.init_layout.addLayout(theta_dot_set_layout)
        self.init_layout.addLayout(gravity_set_layout)
        self.init_layout.addLayout(mu_set_layout)
        self.init_layout.addLayout(L_set_layout)

        self.init_layout.addStretch(1)

        self.init_layout.addWidget(self.combo)
        self.init_layout.addWidget(self.function_plot)

        self.init_layout.addStretch(1)


        # window layout
        self.window_layout = QHBoxLayout()
        self.window_layout.addStretch(1)
        self.window_layout.addLayout(self.init_layout)

        self.set_widget = QWidget()
        self.set_widget.setLayout(self.window_layout)
        self.setCentralWidget(self.set_widget)
        self.set_widget.show()

        self.time_list = []
        self.theta_list = []
        self.theta_dot_list = []


    def update_position(self):
        if self.time_list[-1] > 1 and (self.theta_dot < 0.0001 and self.theta_dot > -0.0001) and ((self.theta < 0.0001 and self.theta > -0.0001) or abs(self.theta_double_dot) < 0.00001):
            self.toggle_animation()
            return
        self.theta_double_dot = -self.g / (self.L_real) * np.sin(self.theta) - self.mu * self.theta_dot
        self.theta_dot += self.theta_double_dot * 0.016
        self.theta += self.theta_dot * 0.016
        if self.theta > np.pi:
            self.theta -= 2 * np.pi

        self.time_list.append(self.time_list[-1] + 0.016)
        self.theta_list.append(self.theta)
        self.theta_dot_list.append(self.theta_dot)
        # self.time_list = self.time_list[-300:]
        # self.theta_list = self.theta_list[-300:]
        if self.combo.currentText() == '角度-时间':
            self.function_plot_data.setData(self.time_list, self.theta_list)
        elif self.combo.currentText() == '角速度-时间':
            self.function_plot_data.setData(self.time_list, self.theta_dot_list)
        elif self.combo.currentText() == '角速度-角度':
            self.function_plot_data.setData(self.theta_list, self.theta_dot_list)

        self.update()    


    def toggle_animation(self):
        if self.begin_button.text() == '开始':
            self.begin_button.setText('停止')
            self.theta = self.sliders[0].value() / 180 * np.pi
            self.theta_dot = self.sliders[1].value() / 180 * np.pi
            self.g = self.sliders[2].value() / 10
            self.mu = self.sliders[3].value() / 1000
            self.L_real = self.sliders[4].value() / 100

            self.theta_double_dot = -self.g / (self.L_real) * np.sin(self.theta) - self.mu * self.theta_dot

            self.timer.start(16)
            for slider in self.sliders:
                slider.setEnabled(False)
            self.combo.setEnabled(False)
            
            self.time_list.clear()
            self.theta_list.clear()
            self.theta_dot_list.clear()

            self.time_list.append(0)
            self.theta_list.append(self.theta)
            self.theta_dot_list.append(self.theta_dot)
        else:
            self.begin_button.setText('开始')
            self.theta_double_dot = 0
            self.theta_dot = 0
            self.theta = 0
            self.update()
            self.timer.stop()
            for slider in self.sliders:
                slider.setEnabled(True)
            self.combo.setEnabled(True)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(255, 0, 0))

        # 计算小球的位置
        ball_x = self.center_x + self.L_animation * np.sin(self.theta)
        ball_y = self.center_y + self.L_animation * np.cos(self.theta)

        ball_x = int(ball_x)
        ball_y = int(ball_y)
        # 绘制小球
        painter.drawEllipse(ball_x - 15, ball_y - 15, 30, 30) 

        # 画一条连接线
        painter.drawLine(self.center_x, self.center_y, ball_x, ball_y)

        # 显示角度和角速度
        painter.drawText(20, 20, 'theta: {:.2f}°'.format(self.theta/np.pi*180))
        # painter.drawText(20, 40, 'theta_dot: {:.2f} rad/s'.format(self.theta_dot))

    
    def function_plot_chose(self):
        if self.combo.currentText() == '角度-时间':
            self.function_plot_data.setData(self.time_list, self.theta_list)
        elif self.combo.currentText() == '角速度-时间':
            self.function_plot_data.setData(self.time_list, self.theta_dot_list)
        elif self.combo.currentText() == '角速度-角度':
            self.function_plot_data.setData(self.theta_list, self.theta_dot_list)
        self.update()


if __name__=='__main__':
    app = QApplication(sys.argv)
    ex = AnimatedWindow()
    ex.show()
    sys.exit(app.exec_())

