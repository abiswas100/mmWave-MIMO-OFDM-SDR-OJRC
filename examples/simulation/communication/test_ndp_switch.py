#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: MIMO OFDM Comm Simulation
# Author: Ceyhun D. Ozkaptan
# Description: The Ohio State University
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
import pmt
from gnuradio import channels
from gnuradio import digital
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import cmath
import mimo_ofdm_jrc
import numpy as np
import ofdm_config  # embedded python module
import os
import random
import string
from gnuradio import qtgui

class mimo_ofdm_comm_sim(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "MIMO OFDM Comm Simulation")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("MIMO OFDM Comm Simulation")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_comm_sim")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.freq = freq = 4e9
        self.rf_freq = rf_freq = freq+20e9
        self.fft_len = fft_len = ofdm_config.N_sc
        self.wavelength = wavelength = 3e8/rf_freq
        self.samp_rate = samp_rate = 125000000
        self.noise_figure_dB = noise_figure_dB = 10
        self.mtu_range = mtu_range = 200
        self.distance = distance = 20
        self.cp_len = cp_len = int(fft_len/4)
        self.tx_multiplier = tx_multiplier = 0.50
        self.theta = theta = 20
        self.sync_length = sync_length = 4*(fft_len+cp_len)
        self.record_comm_stats = record_comm_stats = False
        self.radar_log_file = radar_log_file = os.getcwd()+"/temp/radar_log.csv"
        self.radar_aided = radar_aided = False
        self.phased_steering = phased_steering = False
        self.period = period = 2000
        self.path_loss = path_loss = 4*cmath.pi*distance/wavelength
        self.noise_var = noise_var = 4e-21*samp_rate*10**(noise_figure_dB/10.0)
        self.mtu_value = mtu_value = mtu_range
        self.mcs = mcs = 3
        self.corr_window_size = corr_window_size = int(fft_len/2)
        self.comm_log_file = comm_log_file = os.getcwd()+"/temp/comm_log.csv"
        self.chan_est_file = chan_est_file = os.getcwd()+"/temp/chan_est.csv"
        self.chan_est = chan_est = 1
        self.N_tx = N_tx = ofdm_config.N_tx
        self.N_rx = N_rx = 4
        self.N_ltf = N_ltf = ofdm_config.N_ltf

        ##################################################
        # Blocks
        ##################################################
        self._tx_multiplier_range = Range(0.01, 10, 0.01, 0.50, 200)
        self._tx_multiplier_win = RangeWidget(self._tx_multiplier_range, self.set_tx_multiplier, 'TX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_multiplier_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._theta_range = Range(-90, 90, 1, 20, 200)
        self._theta_win = RangeWidget(self._theta_range, self.set_theta, 'Receiver Angle', "counter_slider", float)
        self.top_grid_layout.addWidget(self._theta_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._record_comm_stats_options = (False, True, )
        # Create the labels list
        self._record_comm_stats_labels = ('False', 'True', )
        # Create the combo box
        self._record_comm_stats_tool_bar = Qt.QToolBar(self)
        self._record_comm_stats_tool_bar.addWidget(Qt.QLabel('Record Comm Stats' + ": "))
        self._record_comm_stats_combo_box = Qt.QComboBox()
        self._record_comm_stats_tool_bar.addWidget(self._record_comm_stats_combo_box)
        for _label in self._record_comm_stats_labels: self._record_comm_stats_combo_box.addItem(_label)
        self._record_comm_stats_callback = lambda i: Qt.QMetaObject.invokeMethod(self._record_comm_stats_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._record_comm_stats_options.index(i)))
        self._record_comm_stats_callback(self.record_comm_stats)
        self._record_comm_stats_combo_box.currentIndexChanged.connect(
            lambda i: self.set_record_comm_stats(self._record_comm_stats_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._record_comm_stats_tool_bar)
        # Create the options list
        self._radar_aided_options = (False, True, )
        # Create the labels list
        self._radar_aided_labels = ('False', 'True', )
        # Create the combo box
        self._radar_aided_tool_bar = Qt.QToolBar(self)
        self._radar_aided_tool_bar.addWidget(Qt.QLabel('Radar-aided Precoding' + ": "))
        self._radar_aided_combo_box = Qt.QComboBox()
        self._radar_aided_tool_bar.addWidget(self._radar_aided_combo_box)
        for _label in self._radar_aided_labels: self._radar_aided_combo_box.addItem(_label)
        self._radar_aided_callback = lambda i: Qt.QMetaObject.invokeMethod(self._radar_aided_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._radar_aided_options.index(i)))
        self._radar_aided_callback(self.radar_aided)
        self._radar_aided_combo_box.currentIndexChanged.connect(
            lambda i: self.set_radar_aided(self._radar_aided_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._radar_aided_tool_bar)
        # Create the options list
        self._phased_steering_options = (False, True, )
        # Create the labels list
        self._phased_steering_labels = ('OFF', 'ON', )
        # Create the combo box
        self._phased_steering_tool_bar = Qt.QToolBar(self)
        self._phased_steering_tool_bar.addWidget(Qt.QLabel('Phased Steering' + ": "))
        self._phased_steering_combo_box = Qt.QComboBox()
        self._phased_steering_tool_bar.addWidget(self._phased_steering_combo_box)
        for _label in self._phased_steering_labels: self._phased_steering_combo_box.addItem(_label)
        self._phased_steering_callback = lambda i: Qt.QMetaObject.invokeMethod(self._phased_steering_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._phased_steering_options.index(i)))
        self._phased_steering_callback(self.phased_steering)
        self._phased_steering_combo_box.currentIndexChanged.connect(
            lambda i: self.set_phased_steering(self._phased_steering_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._phased_steering_tool_bar)
        self._period_range = Range(100, 2000, 100, 2000, 200)
        self._period_win = RangeWidget(self._period_range, self.set_period, 'Enable Period', "counter_slider", int)
        self.top_grid_layout.addWidget(self._period_win)
        # Create the options list
        self._mcs_options = [0, 1, 2, 3, 4, 5]
        # Create the labels list
        self._mcs_labels = ["BPSK 1/2", "BPSK 3/4", "QPSK 1/2", "QPSK 3/4", "16QAM 1/2","16QAM 3/4" ]
        # Create the combo box
        # Create the radio buttons
        self._mcs_group_box = Qt.QGroupBox('Modulation and Coding Scheme' + ": ")
        self._mcs_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._mcs_button_group = variable_chooser_button_group()
        self._mcs_group_box.setLayout(self._mcs_box)
        for i, _label in enumerate(self._mcs_labels):
            radio_button = Qt.QRadioButton(_label)
            self._mcs_box.addWidget(radio_button)
            self._mcs_button_group.addButton(radio_button, i)
        self._mcs_callback = lambda i: Qt.QMetaObject.invokeMethod(self._mcs_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._mcs_options.index(i)))
        self._mcs_callback(self.mcs)
        self._mcs_button_group.buttonClicked[int].connect(
            lambda i: self.set_mcs(self._mcs_options[i]))
        self.top_grid_layout.addWidget(self._mcs_group_box, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._chan_est_options = [0,  1]
        # Create the labels list
        self._chan_est_labels = ["LS",  "STA"]
        # Create the combo box
        # Create the radio buttons
        self._chan_est_group_box = Qt.QGroupBox('Channel Estimation Algorithm' + ": ")
        self._chan_est_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._chan_est_button_group = variable_chooser_button_group()
        self._chan_est_group_box.setLayout(self._chan_est_box)
        for i, _label in enumerate(self._chan_est_labels):
            radio_button = Qt.QRadioButton(_label)
            self._chan_est_box.addWidget(radio_button)
            self._chan_est_button_group.addButton(radio_button, i)
        self._chan_est_callback = lambda i: Qt.QMetaObject.invokeMethod(self._chan_est_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._chan_est_options.index(i)))
        self._chan_est_callback(self.chan_est)
        self._chan_est_button_group.buttonClicked[int].connect(
            lambda i: self.set_chan_est(self._chan_est_options[i]))
        self.top_grid_layout.addWidget(self._chan_est_group_box, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0_2_0 = qtgui.time_sink_c(
            (fft_len+cp_len)*15, #size
            1, #samp_rate
            "RX FRAME", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_2_0.set_update_time(0.1)
        self.qtgui_time_sink_x_0_2_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_2_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_2_0.enable_tags(True)
        self.qtgui_time_sink_x_0_2_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0, 200, 0, "frame_start")
        self.qtgui_time_sink_x_0_2_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_2_0.enable_grid(True)
        self.qtgui_time_sink_x_0_2_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_2_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_2_0.enable_stem_plot(False)

        self.qtgui_time_sink_x_0_2_0.disable_legend()

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [2, 2, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [0.6, 0.6, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_2_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_2_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_2_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_2_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_2_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_2_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_2_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_2_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_2_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_2_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_2_0_win, 7, 0, 1, 1)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._mtu_range_range = Range(0, 300, 50, 200, 200)
        self._mtu_range_win = RangeWidget(self._mtu_range_range, self.set_mtu_range, 'MTU Range', "counter_slider", int)
        self.top_grid_layout.addWidget(self._mtu_range_win)
        self.mimo_ofdm_jrc_zero_pad_0_0_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, 6*(fft_len+cp_len)+10)
        self.mimo_ofdm_jrc_zero_pad_0_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, 6*(fft_len+cp_len)+10)
        self.mimo_ofdm_jrc_zero_pad_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, 6*(fft_len+cp_len)+10)
        self.mimo_ofdm_jrc_zero_pad_0 = mimo_ofdm_jrc.zero_pad(False, 5, 6*(fft_len+cp_len)+10)
        self.mimo_ofdm_jrc_stream_encoder_1 = mimo_ofdm_jrc.stream_encoder(mcs, ofdm_config.N_data, 0, False)
        self.mimo_ofdm_jrc_stream_decoder_0 = mimo_ofdm_jrc.stream_decoder(len(ofdm_config.data_subcarriers), comm_log_file, record_comm_stats, False)
        self.mimo_ofdm_jrc_ndp_generator_1 = mimo_ofdm_jrc.ndp_generator()
        self.mimo_ofdm_jrc_moving_avg_0 = mimo_ofdm_jrc.moving_avg(corr_window_size, 1, 16000, False)
        self.mimo_ofdm_jrc_mimo_precoder_0 = mimo_ofdm_jrc.mimo_precoder(fft_len, N_tx, 1, ofdm_config.data_subcarriers, ofdm_config.pilot_subcarriers, ofdm_config.pilot_symbols, ofdm_config.l_stf_ltf_64, ofdm_config.ltf_mapped_sc__ss_sym, chan_est_file, False, radar_log_file, radar_aided, phased_steering, False, "packet_len",  True)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0 = mimo_ofdm_jrc.mimo_ofdm_equalizer(chan_est, rf_freq, samp_rate, fft_len, cp_len, ofdm_config.data_subcarriers, ofdm_config.pilot_subcarriers, ofdm_config.pilot_symbols, ofdm_config.l_stf_ltf_64[3], ofdm_config.ltf_mapped_sc__ss_sym, N_tx, chan_est_file, "", False, False)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0.set_min_output_buffer(80000)
        self.mimo_ofdm_jrc_frame_sync_0 = mimo_ofdm_jrc.frame_sync(fft_len, cp_len, sync_length, ofdm_config.l_ltf_fir, False)
        self.mimo_ofdm_jrc_frame_detector_0 = mimo_ofdm_jrc.frame_detector(fft_len, cp_len, 0.6, 10, (len(ofdm_config.l_stf_ltf_64)+N_tx)*(fft_len+cp_len), False)
        self.fft_vxx_0_2_0_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 2)
        self.fft_vxx_0_2_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 2)
        self.fft_vxx_0_2 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 2)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_len, True, window.rectangular(fft_len), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 2)
        self.digital_ofdm_cyclic_prefixer_0_0_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=np.sqrt(noise_var),
            frequency_offset=0.02/fft_len,
            epsilon=1.0,
            taps=[1.0],
            noise_seed=0,
            block_tags=True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_len)
        self.blocks_socket_pdu_1 = blocks.socket_pdu('UDP_CLIENT', '127.0.0.1', '52002', 5000, False)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_1_0_0_0 = blocks.multiply_const_cc((1/path_loss)*cmath.exp(3j*cmath.pi*np.sin(np.deg2rad(theta))))
        self.blocks_multiply_const_vxx_1_0_0 = blocks.multiply_const_cc((1/path_loss)*cmath.exp(2j*cmath.pi*np.sin(np.deg2rad(theta))))
        self.blocks_multiply_const_vxx_1_0 = blocks.multiply_const_cc((1/path_loss)*cmath.exp(1j*cmath.pi*np.sin(np.deg2rad(theta))))
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_cc(1/path_loss)
        self.blocks_multiply_const_vxx_0_0_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_moving_average_xx_1_0 = blocks.moving_average_ff(int(1.5*corr_window_size), 1/1.5, 16000, 1)
        self.blocks_moving_average_xx_1_0.set_processor_affinity([3, 4])
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.from_long(1), period)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, int(fft_len/4))
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, sync_length)
        self.blocks_conjugate_cc_0 = blocks.conjugate_cc()
        self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_add_xx_0_0 = blocks.add_vcc(1)
        self.blocks_abs_xx_0 = blocks.abs_ff(1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.mimo_ofdm_jrc_ndp_generator_1, 'enable'))
        self.msg_connect((self.mimo_ofdm_jrc_ndp_generator_1, 'out'), (self.mimo_ofdm_jrc_stream_encoder_1, 'pdu_in'))
        self.msg_connect((self.mimo_ofdm_jrc_stream_decoder_0, 'sym'), (self.blocks_socket_pdu_1, 'pdus'))
        self.connect((self.blocks_abs_xx_0, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.blocks_add_xx_0_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.blocks_moving_average_xx_1_0, 0))
        self.connect((self.blocks_conjugate_cc_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.mimo_ofdm_jrc_frame_sync_0, 1))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_conjugate_cc_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.mimo_ofdm_jrc_frame_detector_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.mimo_ofdm_jrc_frame_detector_0, 2))
        self.connect((self.blocks_moving_average_xx_1_0, 0), (self.blocks_abs_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mimo_ofdm_jrc_zero_pad_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_add_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1_0, 0), (self.blocks_add_xx_0_0, 1))
        self.connect((self.blocks_multiply_const_vxx_1_0_0, 0), (self.blocks_add_xx_0_0, 2))
        self.connect((self.blocks_multiply_const_vxx_1_0_0_0, 0), (self.blocks_add_xx_0_0, 3))
        self.connect((self.blocks_multiply_xx_0, 0), (self.mimo_ofdm_jrc_moving_avg_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_complex_to_mag_squared_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.channels_channel_model_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0, 0))
        self.connect((self.fft_vxx_0_2, 0), (self.digital_ofdm_cyclic_prefixer_0_0, 0))
        self.connect((self.fft_vxx_0_2_0, 0), (self.digital_ofdm_cyclic_prefixer_0_0_0, 0))
        self.connect((self.fft_vxx_0_2_0_0, 0), (self.digital_ofdm_cyclic_prefixer_0_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_frame_detector_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.mimo_ofdm_jrc_frame_detector_0, 0), (self.mimo_ofdm_jrc_frame_sync_0, 0))
        self.connect((self.mimo_ofdm_jrc_frame_detector_0, 0), (self.qtgui_time_sink_x_0_2_0, 0))
        self.connect((self.mimo_ofdm_jrc_frame_sync_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0, 0), (self.mimo_ofdm_jrc_stream_decoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 1), (self.fft_vxx_0_2, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 2), (self.fft_vxx_0_2_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 3), (self.fft_vxx_0_2_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_moving_avg_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.mimo_ofdm_jrc_moving_avg_0, 0), (self.mimo_ofdm_jrc_frame_detector_0, 1))
        self.connect((self.mimo_ofdm_jrc_stream_decoder_0, 0), (self.blocks_null_sink_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_stream_encoder_1, 0), (self.mimo_ofdm_jrc_mimo_precoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0, 0), (self.blocks_multiply_const_vxx_1_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0_0, 0), (self.blocks_multiply_const_vxx_1_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0_0_0, 0), (self.blocks_multiply_const_vxx_1_0_0_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_comm_sim")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.set_rf_freq(self.freq+20e9)

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.set_wavelength(3e8/self.rf_freq)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0.set_frequency(self.rf_freq)

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_corr_window_size(int(self.fft_len/2))
        self.set_cp_len(int(self.fft_len/4))
        self.set_sync_length(4*(self.fft_len+self.cp_len))
        self.blocks_delay_0_0.set_dly(int(self.fft_len/4))
        self.channels_channel_model_0.set_frequency_offset(0.02/self.fft_len)

    def get_wavelength(self):
        return self.wavelength

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength
        self.set_path_loss(4*cmath.pi*self.distance/self.wavelength)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_noise_var(4e-21*self.samp_rate*10**(self.noise_figure_dB/10.0))
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0.set_bandwidth(self.samp_rate)

    def get_noise_figure_dB(self):
        return self.noise_figure_dB

    def set_noise_figure_dB(self, noise_figure_dB):
        self.noise_figure_dB = noise_figure_dB
        self.set_noise_var(4e-21*self.samp_rate*10**(self.noise_figure_dB/10.0))

    def get_mtu_range(self):
        return self.mtu_range

    def set_mtu_range(self, mtu_range):
        self.mtu_range = mtu_range
        self.set_mtu_value(self.mtu_range)

    def get_distance(self):
        return self.distance

    def set_distance(self, distance):
        self.distance = distance
        self.set_path_loss(4*cmath.pi*self.distance/self.wavelength)

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len
        self.set_sync_length(4*(self.fft_len+self.cp_len))

    def get_tx_multiplier(self):
        return self.tx_multiplier

    def set_tx_multiplier(self, tx_multiplier):
        self.tx_multiplier = tx_multiplier
        self.blocks_multiply_const_vxx_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0_0.set_k(self.tx_multiplier)

    def get_theta(self):
        return self.theta

    def set_theta(self, theta):
        self.theta = theta
        self.blocks_multiply_const_vxx_1_0.set_k((1/self.path_loss)*cmath.exp(1j*cmath.pi*np.sin(np.deg2rad(self.theta))))
        self.blocks_multiply_const_vxx_1_0_0.set_k((1/self.path_loss)*cmath.exp(2j*cmath.pi*np.sin(np.deg2rad(self.theta))))
        self.blocks_multiply_const_vxx_1_0_0_0.set_k((1/self.path_loss)*cmath.exp(3j*cmath.pi*np.sin(np.deg2rad(self.theta))))

    def get_sync_length(self):
        return self.sync_length

    def set_sync_length(self, sync_length):
        self.sync_length = sync_length
        self.blocks_delay_0.set_dly(self.sync_length)

    def get_record_comm_stats(self):
        return self.record_comm_stats

    def set_record_comm_stats(self, record_comm_stats):
        self.record_comm_stats = record_comm_stats
        self._record_comm_stats_callback(self.record_comm_stats)
        self.mimo_ofdm_jrc_stream_decoder_0.set_stats_record(self.record_comm_stats)

    def get_radar_log_file(self):
        return self.radar_log_file

    def set_radar_log_file(self, radar_log_file):
        self.radar_log_file = radar_log_file

    def get_radar_aided(self):
        return self.radar_aided

    def set_radar_aided(self, radar_aided):
        self.radar_aided = radar_aided
        self._radar_aided_callback(self.radar_aided)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_radar_aided(self.radar_aided)

    def get_phased_steering(self):
        return self.phased_steering

    def set_phased_steering(self, phased_steering):
        self.phased_steering = phased_steering
        self._phased_steering_callback(self.phased_steering)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_phased_steering(self.phased_steering)

    def get_period(self):
        return self.period

    def set_period(self, period):
        self.period = period
        self.blocks_message_strobe_0.set_period(self.period)

    def get_path_loss(self):
        return self.path_loss

    def set_path_loss(self, path_loss):
        self.path_loss = path_loss
        self.blocks_multiply_const_vxx_1.set_k(1/self.path_loss)
        self.blocks_multiply_const_vxx_1_0.set_k((1/self.path_loss)*cmath.exp(1j*cmath.pi*np.sin(np.deg2rad(self.theta))))
        self.blocks_multiply_const_vxx_1_0_0.set_k((1/self.path_loss)*cmath.exp(2j*cmath.pi*np.sin(np.deg2rad(self.theta))))
        self.blocks_multiply_const_vxx_1_0_0_0.set_k((1/self.path_loss)*cmath.exp(3j*cmath.pi*np.sin(np.deg2rad(self.theta))))

    def get_noise_var(self):
        return self.noise_var

    def set_noise_var(self, noise_var):
        self.noise_var = noise_var
        self.channels_channel_model_0.set_noise_voltage(np.sqrt(self.noise_var))

    def get_mtu_value(self):
        return self.mtu_value

    def set_mtu_value(self, mtu_value):
        self.mtu_value = mtu_value

    def get_mcs(self):
        return self.mcs

    def set_mcs(self, mcs):
        self.mcs = mcs
        self._mcs_callback(self.mcs)
        self.mimo_ofdm_jrc_stream_encoder_1.set_mcs(self.mcs)

    def get_corr_window_size(self):
        return self.corr_window_size

    def set_corr_window_size(self, corr_window_size):
        self.corr_window_size = corr_window_size
        self.blocks_moving_average_xx_1_0.set_length_and_scale(int(1.5*self.corr_window_size), 1/1.5)
        self.mimo_ofdm_jrc_moving_avg_0.set_length_and_scale(self.corr_window_size, 1)

    def get_comm_log_file(self):
        return self.comm_log_file

    def set_comm_log_file(self, comm_log_file):
        self.comm_log_file = comm_log_file

    def get_chan_est_file(self):
        return self.chan_est_file

    def set_chan_est_file(self, chan_est_file):
        self.chan_est_file = chan_est_file

    def get_chan_est(self):
        return self.chan_est

    def set_chan_est(self, chan_est):
        self.chan_est = chan_est
        self._chan_est_callback(self.chan_est)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0.set_estimator(self.chan_est)

    def get_N_tx(self):
        return self.N_tx

    def set_N_tx(self, N_tx):
        self.N_tx = N_tx

    def get_N_rx(self):
        return self.N_rx

    def set_N_rx(self, N_rx):
        self.N_rx = N_rx

    def get_N_ltf(self):
        return self.N_ltf

    def set_N_ltf(self, N_ltf):
        self.N_ltf = N_ltf



def main(top_block_cls=mimo_ofdm_comm_sim, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()
    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()