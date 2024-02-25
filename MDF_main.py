# MDF Viewer 
# MDF(1) - represents the mf4 file
#  ->Channel group 0  (cg)
#  ->->Channel signal (ch)
#  ->->...

from PySide6.QtCore import (Qt,QRect, Slot, Signal, QPoint)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QFileDialog, QTreeWidgetItem, QTreeWidgetItemIterator, QTableWidgetItem, QDialogButtonBox)
from PySide6.QtGui import (QFont,QBrush,QColor)
from ui.MDF_main_window import Ui_MainWindow
from ui.Channel_cfg import Ui_Channel_Cfg
from ui.Sig_Integration import Ui_Sig_Integration
from lib.MDF_pars import (extract_channel_name, extract_non_IO_channel_name, chennel_type)
from lib.Cursor import (Cursor)
from lib.ChannHeader import (ChannHeader)
import sys, mdfreader, os
import numpy as np
import pandas as pd
import pyqtgraph as pg
from datetime import datetime
import yaml 
from yaml import load
import copy
from scipy import integrate, ndimage, signal
import shutil

class Cfg_Ch_Window(QMainWindow):
    closed = Signal()
    def __int__(self):
        Ui_Channel_Cfg.__init__(self)

    @Slot()
    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
        
class Sig_Integration(QMainWindow):
    closed = Signal()
    def __int__(self):
        Ui_Sig_Integration.__init__(self)

    @Slot()
    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

class MainWindow(Ui_MainWindow, Ui_Channel_Cfg, QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #super().__init__()
        self.setupUi(self)
        #Adding functionalities to GUI
        self.pushButton.clicked.connect(self.clear)
        self.pushButton_2.clicked.connect(self.fit_plot_xy)
        self.pushButton_3.clicked.connect(self.add_x1_cursor)
        self.actionFit_Window.triggered.connect(self.fit_plot_xy)
        self.pushButton_4.clicked.connect(self.add_x2_cursor)
        self.actionInfo.triggered.connect(self.help)
        self.actionOpen.triggered.connect(self.file_open)
        self.pushButton_5.clicked.connect(self.scale_y)
        self.actionChannel_name.triggered.connect(self.cfg_all_channels_click)
        self.actionIntegration.triggered.connect(self.sig_integration)
        self.stack_all_btn.clicked.connect(self.stack_all)
        self.actionStack_all.triggered.connect(self.stack_all)
        self.Shift_Sig_Button.clicked.connect(self.shift_signal_x_axis)
        self.actionLoad_Configuration.triggered.connect(self.load_configuration)
        self.actionSave_Configuration.triggered.connect(self.save_configuration)
        
     
        #prohibit of opening of more then one window
        self.cfg_window=None
        self.sig_integ_window=None
       
        #Verion
        self.ver = "MDF Viewer v0.1"
        #Set Main Window Title
        self.setWindowTitle(self.ver)
        
        #buffer ploted channels
        self.plots = []
        #common time base
        self.time_com = []
        #buffer plot object : x-Time, y-I/O signal value  
        self.plots_obj = []
        self.ViewBoxes = []
        self.p1=self.graphicsView.plotItem 
        self.req_channels = []  
        self.legend = self.p1.addLegend()
        #Hold parsed MDF channels from dSPACE mdf files
        #TODO self.channel_dict is used as global in hold_view(). Implement as local channel_dict
        self.channel_dict={}
        self.channel_dict_set=[]
        #Dict used for channel config. The idea is to present always the short channel names
        self.cfg_sig_dict_set=[]
        self.cfg_sig_dict= {}
        self.values_cfg = []
        self.values_cfg_set = []
        self.keys_cfg=[]
        self.keys_cfg_set=[]
        #Dict used to show always short name and long full channel path in case usage of short name is disabled
        self.tbl_channel_dict_set=[]
        self.myHeader=0
        #Dict used to store configuration to yaml
        self.selected_signals_yml ={}
        self.cfg_sig_dict_set_yml=[]
        self.values_cfg_yml = []
        self.values_cfg_set_yml = []
        self.keys_cfg_yml=[]
        self.keys_cfg_set_yml=[]
        #Calculated signals : Integration
        self.intg_sig_dict= {}
        self.intg_sig_dict_set=[]
        self.values_intg = []
        self.values_intg_set = []
        self.keys_intg=[]
        self.keys_intg_set=[]
        self.tbl_index_integ=0
        #Flag to disable the dictionary cannel name and usage of full channel path instead
        try:
            self.confing_ch_load()
            self.load_selected_signals()
        except:
            self.all_sig_sel=True
            
        #List of imported MDF files 
        self.mdf_ch_set = []
        #Curent MDF Channel set
        self.mdf_ch = 0
        #Hold path to the imported MDF files
        self.mdf_file_in_set = []
        #Trace top level MDF name e.g. MDF(1) for the first imported MDF file
        self.mdf_toplevel_item=[]
        #Trace channel group e.g. Channel group 0...
        self.mdf_cg_set=[]
        #Splitter list / plot
        self.splitter_list_plot.setStretchFactor(1,2)
        self.splitter_list_plot.splitterMoved.connect(self.splliter_moved)
        
        # X axis Min/Max
        self.start_x=0
        self.stop_x=0
        
        #Add grid
        self.graphicsView.showGrid(x = True, y = True, alpha = 0.3)
        
        #Plot
        self.p1.vb.sigResized.connect(lambda:self.updateViews())
        self.p1.vb.sigRangeChangedManually.connect(self.x_range_hold)
        self.color_cnt=0
        self.LINECOLORS = ('r', 'g', 'b', 'c', 'm', 'y','w')
        
        #Tree
        self.treeWidget.itemClicked.connect(self.tree_element_click)
        self.treeWidget.itemDoubleClicked.connect(self.tree_element_dbclick)
        self.treeWidget.itemSelectionChanged.connect(self.change_signal_focus)
        
        #Tree top level items
        self.top_level_items=[]
        self.treeWidget.setHeaderItem(QTreeWidgetItem(['Channels']))
        self.treeWidget.itemClicked.connect(self.get_mdf_creation_date)
        
        #LCD Disply
        self.text_LCD="0.0"
        self.splliter_moved()
        
        # X1 Cursor
        self.X1_marker = Cursor(
            pos=0,
            angle=90,
            pen='y',
            movable=True)
        self.X1_marker.setValue(0.)
        self.X1_marker.setZValue(1000)
        # add label to X1 cursor
        self.X1_marker_lab = pg.InfLineLabel(
            line = self.X1_marker,
            text="0",
            movable=True,
            position=0.5)
        # X2 marker
        self.X2_marker = Cursor(
            pos=10,
            angle=90,
            pen='y',
            movable=True)
        self.X2_marker.setValue(0.)
        self.X2_marker.setZValue(1000)
        # add label to X2 cursor
        self.X2_marker_lab = pg.InfLineLabel(
            line = self.X2_marker,
            text="0",
            movable=True,
            position=0.5)
#Shift sig
    def shift_signal_x_axis(self):
        [current_id, channel_req, mdf_set_num, is_top_level, cg_id]=self.req_curr_chann()
         
        self.remove_plotted_sig(channel_req,mdf_set_num,current_id)
        Channel_y=self.y_signal_type(channel_req,mdf_set_num,cg_id) 
        #Get the time base i.e. 'Periodic Task 1'
        Time_sig=self.mdf_ch_set[mdf_set_num].get_channel_data(list(self.channel_dict_set[mdf_set_num][cg_id].items())[0][0])
        #Find the Timestamp for scaling
        s = pd.Series(Time_sig)
        difftime=s.diff(periods=-1) 
        if (round(abs(difftime[10]),4)) is None:
            time_const=1
        else:
            time_const=1/round(abs(difftime[10]),4)
            
        #Shift in direction of Y - axis                      
        shift=int(self.Shift_Sig_X.value() * time_const)   
        Channel_y=ndimage.shift(Channel_y, shift, output=None, order=3, mode='constant', cval=0.0, prefilter=True)
        #Shift in direction of Y - axis
        y_val=self.Shift_Sig_Y.value()
        Channel_y=np.add(Channel_y, y_val)
        #Plot signal
        self.plot_signal_vb(Time_sig,Channel_y,channel_req,mdf_set_num, current_id)
        return
    
    def plot_signal_vb(self,Time_sig,Channel_y,channel_req,mdf_set_num, current_id):
        self.xcoords = Time_sig
        self.yvalues = Channel_y
        
        #Make unique id number for channel as more MDF files can be imported
        uid_channel_id=channel_req+str(mdf_set_num)
        
        #If already ploted exit 
        for i, obj in enumerate(self.req_channels): 
            if obj == uid_channel_id:
                print("already ploted")
                return   
        else:
            # Highlight current item
            # Color Name: Water RGB: (216, 242, 255)
            current_id.setBackground(0,QBrush(QColor( 216, 242, 255, 255)))    
            #self.req_channels.append(channel_req)
            self.req_channels.append(uid_channel_id)
        if self.color_cnt<len(self.LINECOLORS):
            pen_color=self.LINECOLORS[self.color_cnt]
            self.color_cnt += 1
        else:
            self.color_cnt=0
            pen_color=self.LINECOLORS[self.color_cnt]
        
        #Ploted object
        channel_req_name = channel_req + ' (' + str(mdf_set_num + 1) + ')'     
        curve =pg.PlotDataItem(Time_sig, Channel_y, name=channel_req_name, pen=pen_color, width=1)  
        
        #Add requested channel 
        self.plots.append(Channel_y)
        self.time_com.append(Time_sig)
        #Add new view box per curve 
        new_vb=pg.ViewBox()
        #Add to the list of active view boxes
        self.ViewBoxes.append(new_vb)  
        self.legend.addItem(curve, curve.name())
        #self.legend.addItem(curve, curve.name())
        self.p1.scene().addItem(new_vb)
        self.p1.getAxis('left').linkToView(new_vb)
        self.p1.getAxis('bottom').linkToView(new_vb)
        new_vb.setGeometry(self.p1.getViewBox().sceneBoundingRect())
        self.plots_obj.append(curve)
        #Take the new x range 
        start_ts = np.amin(Time_sig)
        stop_ts = np.amax(Time_sig)
        #Keep the current zoom when adding new signal to the plot widget
        startx= max( self.start_x, start_ts)
        stopx = min(self.stop_x, stop_ts)
        new_vb.setXRange(startx, stopx)
        new_vb.addItem(curve)
        new_vb.setXLink(self.p1)
        
        self.current_ch.setHtml(
                "<b>"+channel_req_name + "="+ "</b>") 
        
        return
#Configuration  

    def set_back_cfg_sctack(self):
    
        self.cfg_sig_dict_set=[]
        self.cfg_sig_dict= {}
        self.values_cfg = []
        self.values_cfg_set = []
        self.keys_cfg=[]
        self.keys_cfg_set=[]
        self.cfg_sig_dict_set_yml=[]
        self.values_cfg_yml = []
        self.values_cfg_set_yml = []
        self.keys_cfg_yml=[]
        self.keys_cfg_set_yml=[]
        return

    def load_configuration(self):    
        # Import MDF file over Menu (File/Open)
        try:
            filter = "yml(*.yml)"
            qfd = QFileDialog()
            path= os.getcwd()+'\\config'
            cfg_yml, _= QFileDialog.getOpenFileName(qfd,'',path, filter)
            if cfg_yml.endswith('.yml'):
                infile=open(cfg_yml, 'r')
                self.selected_signals_yml = yaml.safe_load(infile)
                #Write into local config yml file
                with open(os.getcwd()+'\\config\selected_ch.yml', 'w') as outfile:
                    yaml.dump(self.selected_signals_yml, outfile, default_flow_style=False)
                    outfile.close()
                #Use the new rules for new drop/file open actions
                self.load_selected_signals()
                

                self.remove_all_tree_items()
                self.refresh_tree_items()
                    
                self.set_back_cfg_sctack()
                self.init_cfg_data_set()
                
            elif (not (cfg_yml and cfg_yml.strip())):
                return False
            else:
                dialog = QMessageBox(self.centralwidget) 
                dialog.setText("Wrong (non-YML) file format!")
                dialog.setFont(QFont('Arial', 15))
                dialog.setStandardButtons(QMessageBox.StandardButton.Close)
                dialog.show()   
                return False              
        except:
                print("Error importing Configuration")
                return
            
    def refresh_tree_items(self):
        for mdf_index, items in enumerate(self.channel_dict_set):
            for dict_set_cg, group_item in enumerate(items):
                self.insert_sig_tree(mdf_index,dict_set_cg)
        
        return
            
    
    def save_configuration(self):
        try:
            qfd = QFileDialog.getExistingDirectory()
        except:
            return
    
        if qfd.find(os.getcwd()+'\\config')!=-1:
            print("Avoid storing into \config as being system folder!")
        else:
            print(qfd)
            if not (qfd and qfd.strip()):
                return
            target_folder=qfd
            
            filename='selected_ch.yml'
            source_folder=os.getcwd()+'\\config'
            for filename in os.listdir(source_folder):
                source_file = os.path.join(source_folder, filename)
                if os.path.isfile(source_file):
                    shutil.copy(source_file, target_folder) 
        return
        
    def config_ch_yaml(self):
        #Write to configuration file 
        if (self.ui.dict_All_Sig_Sel.isChecked()):   
         data = dict(
            All_Sig_Sel = True
            )
        else:  
            data = dict(
            All_Sig_Sel = False
            )
            
        with open(os.getcwd()+'\\config\confg.yml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
        outfile.close()
        
        return
            
    def confing_ch_load(self):
        infile=open(os.getcwd()+'\\config\confg.yml', 'r')
        dict_yml = yaml.safe_load(infile)
        
        if dict_yml['All_Sig_Sel']  is False:
            self.all_sig_sel = False
        else:
            self.all_sig_sel = True
             
    def load_selected_signals(self):
        if not self.all_sig_sel:
            infile=open(os.getcwd()+'\\config\selected_ch.yml', 'r')
            self.selected_signals_yml = yaml.safe_load(infile)
        return
    
    def write_yaml(self):
        merge_selected_sig = {}
        for i in range (len(self.cfg_sig_dict_set_yml)):
            for obj in self.cfg_sig_dict_set_yml[i]:
                merge_selected_sig.update(obj) 
        #Save selected signals
        with open(os.getcwd()+'\\config\selected_ch.yml', 'w') as outfile:
            yaml.dump(merge_selected_sig, outfile, default_flow_style=False)
        outfile.close()
        #Use the new rules for new drop/file open actions
        self.load_selected_signals()
        return    
    
    def ena_act_menu(self):
        self.actionChannel_name.setEnabled(True)
        self.actionStack_all.setEnabled(True)
        self.actionFit_Window.setEnabled(True)
        self.actionIntegration.setEnabled(True)
        return    
    
    def cfg_all_channels_click(self):
        #Prevent opening of multiple channel configuration windows 
        if self.cfg_window is None:
            self.cfg_window = Cfg_Ch_Window(self)
        else:
            return
        self.ui = Ui_Channel_Cfg()
        if  (self.all_sig_sel):
            self.ui.setupUi(self.cfg_window)
        else:
            self.ui.setupUi(self.cfg_window)
            self.ui.dict_All_Sig_Sel.setCheckState(Qt.Unchecked)
        
        if self.all_sig_sel:
           self.ui.Channel_cfg_ButtonBox.setStandardButtons(QDialogButtonBox.Cancel)
        else:
           self.ui.Channel_cfg_ButtonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        
        self.ui.Channel_cfg_ButtonBox.accepted.connect(self.apply_cfg)
        self.ui.Channel_cfg_ButtonBox.rejected.connect(self.reject)
        self.ui.Channel_cfg_ButtonBox.ButtonRole.ApplyRole
        self.cfg_window.closed.connect(self.cfg_closeEvent)
        
        for i in range (len(self.mdf_toplevel_item)):
            self.ui.listMdf.insertItem(i, self.mdf_toplevel_item[i])
        
        for i in range (len(self.mdf_cg_set[0])):
            self.ui.listCg.insertItem(i, self.mdf_cg_set[0][i])
             
        self.ui.listMdf.itemClicked.connect(self.update_conf_cg_list)   
        self.ui.listMdf.itemSelectionChanged.connect(self.update_conf_cg_list)
        self.ui.listCg.itemClicked.connect(self.fill_tbl_cfg)   
        self.ui.listCg.itemSelectionChanged.connect(self.fill_tbl_cfg)
        #Table events
        self.ui.tableChannels.itemClicked.connect(self.table_cfg_element_cnd)
        self.ui.dict_All_Sig_Sel.clicked.connect(self.chk_st_All_Sig_Sel)
        self.ui.listMdf.setCurrentRow(0)
        self.ui.listCg.setCurrentRow(0)
        self.cfg_window.show()
        self.cfg_window.setWindowTitle("Channel mapping")
        
    def table_cfg_element_cnd(self, item):
              
        dict_set=self.ui.listMdf.currentRow()
        dict_set_cg=self.ui.listCg.currentRow()
        it = self.treeWidget.topLevelItem((self.ui.listMdf.currentRow())) 
        cg_ch= it.child(dict_set_cg)
        channel_req=self.ui.tableChannels.item(item.row(),1).text()
        channel_name =  channel_req  
        channel_name_ok=self.tbl_channel_dict_set[dict_set][dict_set_cg].get(channel_name,-1)
        org_ch_name=list(self.channel_dict_set[dict_set][dict_set_cg].items())[item.row()][0]
        #org_ch_name_active=self.channel_dict_set[dict_set][dict_set_cg].get(channel_name,-1)
        try:
            org_ch_name_active=list(self.cfg_sig_dict_set_yml[dict_set][dict_set_cg].keys()).index(org_ch_name)
        except:
            print("Key not found")
            org_ch_name_active=-1
            
            
        check_item=self.ui.tableChannels.item(item.row(), 0)
        if (channel_name_ok!=-1):
            #Find Key in dictionary
            if (check_item.checkState() == Qt.Checked) and not any([True for k,v in self.cfg_sig_dict_set[dict_set][dict_set_cg].items() if k == channel_name]):
                for mdf_index, items in enumerate(self.channel_dict_set): 
                    for dict_set_cg, group_item in enumerate(items):
                        Channel_y=self.mdf_ch_set[mdf_index].get_channel_data(self.channel_dict_set[mdf_index][dict_set_cg].get(channel_req))
                        try:
                            #Find index in dictionary 
                            val_index=list(self.tbl_channel_dict_set[mdf_index][dict_set_cg].keys()).index(channel_name)
                            self.keys_cfg_set[mdf_index][dict_set_cg].append(channel_name)
                            self.values_cfg_set[mdf_index][dict_set_cg].append(Channel_y)
                            #yml
                            self.keys_cfg_set_yml[mdf_index][dict_set_cg].append(channel_name)
                                
                            self.values_cfg_set_yml[mdf_index][dict_set_cg].append(list(self.tbl_channel_dict_set[mdf_index][dict_set_cg].items())[val_index][1])
                            self.cfg_sig_dict_set[mdf_index][dict_set_cg] = {self.keys_cfg_set[mdf_index][dict_set_cg][index]: self.values_cfg_set[mdf_index][dict_set_cg][index] for index in range(len(self.keys_cfg_set[mdf_index][dict_set_cg]))}
                            self.cfg_sig_dict_set_yml[mdf_index][dict_set_cg] = {self.keys_cfg_set_yml[mdf_index][dict_set_cg][index]: self.values_cfg_set_yml[mdf_index][dict_set_cg][index] for index in range(len(self.keys_cfg_set_yml[mdf_index][dict_set_cg]))}
                            cg_ch_item=[channel_name]
                            ch_item=QTreeWidgetItem(cg_ch_item)  
                            cg_item=self.top_level_items[mdf_index].child(dict_set_cg)
                            cg_item.addChild(ch_item)
                        except:
                            print("Key not found -> exit")
                            continue 
                            
            elif (check_item.checkState() == Qt.Unchecked and any([True for k,v in self.cfg_sig_dict_set[dict_set][dict_set_cg].items() if k == channel_name])):
                 #Remove the item form tree and memory
                 self.remove_item(channel_name)
                
            #Update the selection rules
            merge_selected_sig={}
            for i in range (len(self.cfg_sig_dict_set_yml)):
                for obj in self.cfg_sig_dict_set_yml[i]:
                    merge_selected_sig.update(obj)
            
            self.selected_signals_yml=copy.deepcopy(merge_selected_sig)                  
            
        else:
            if(check_item.checkState() == Qt.Checked) and (org_ch_name_active==-1) :
                for mdf_index, items in enumerate(self.channel_dict_set):
                    try:
                        self.channel_dict_set[mdf_index][dict_set_cg]= {channel_name if k == org_ch_name else k:v for k,v in self.channel_dict_set[mdf_index][dict_set_cg].items()}
                        self.tbl_channel_dict_set= copy.deepcopy(self.channel_dict_set) 
                    except:
                        print("Key not found -> Update new Key")
                        continue 
               
                for mdf_index, items in enumerate(self.channel_dict_set):
                    for dict_set_cg, group_item in enumerate(items):
                        Channel_y=self.mdf_ch_set[mdf_index].get_channel_data(self.channel_dict_set[mdf_index][dict_set_cg].get(channel_req))
                        try:
                            #Find index in dictionary 
                            val_index=list(self.tbl_channel_dict_set[mdf_index][dict_set_cg].keys()).index(channel_name)
                            self.keys_cfg_set[mdf_index][dict_set_cg].append(channel_name)
                            self.values_cfg_set[mdf_index][dict_set_cg].append(Channel_y)
                            #yml
                            self.keys_cfg_set_yml[mdf_index][dict_set_cg].append(channel_name)
                                
                            self.values_cfg_set_yml[mdf_index][dict_set_cg].append(list(self.tbl_channel_dict_set[mdf_index][dict_set_cg].items())[val_index][1])
                            self.cfg_sig_dict_set[mdf_index][dict_set_cg] = {self.keys_cfg_set[mdf_index][dict_set_cg][index]: self.values_cfg_set[mdf_index][dict_set_cg][index] for index in range(len(self.keys_cfg_set[mdf_index][dict_set_cg]))}
                            self.cfg_sig_dict_set_yml[mdf_index][dict_set_cg] = {self.keys_cfg_set_yml[mdf_index][dict_set_cg][index]: self.values_cfg_set_yml[mdf_index][dict_set_cg][index] for index in range(len(self.keys_cfg_set_yml[mdf_index][dict_set_cg]))}
                            cg_ch_item=[channel_name]
                            ch_item=QTreeWidgetItem(cg_ch_item)  
                            cg_item=self.top_level_items[mdf_index].child(dict_set_cg)
                            cg_item.addChild(ch_item)
                        except:
                            print("Key not found -> Add to tree")
                            continue                     
                    self.update_rules()
  
            elif (check_item.checkState() == Qt.Unchecked):
                #Remove signal before rename action
                self.remove_item(org_ch_name)
                return            
        return   
    
    def remove_all_tree_items(self):
        cfg_sig_dict_set=copy.deepcopy(self.cfg_sig_dict_set)   
        for mdf_index, items in enumerate(cfg_sig_dict_set):
            
            for dict_set_cg, group_item in enumerate(items):
            
                for ch_index, ch_it in enumerate(group_item): 
                    
                        channel_name=list(cfg_sig_dict_set[mdf_index][dict_set_cg].items())[ch_index][0]
                        index = list(cfg_sig_dict_set[mdf_index][dict_set_cg]).index(channel_name)
                        it= self.treeWidget.topLevelItem(mdf_index)
                        #Find index based on name
                        it_items = QTreeWidgetItemIterator(it)
                        index_child=0
                        index=0
                        channel_item_flg=False
                        #TODO: Improve algorithm for indexing
                        while it_items.value():
                            child_item=it_items.value()
                            if (child_item.text(0).find("Channel group")!= -1):
                                index_child=0
                                channel_item_flg=True
                            elif channel_item_flg:
                                index_child+=1
                                if child_item.text(0) == channel_name:
                                    index=index_child-1
                                    break
                        
                            it_items += 1 
                        
                        cg_ch = it.child(dict_set_cg)
                        ch_it= cg_ch.child(index)
                                
                        it.removeChild(ch_it)
                         
        self.set_back_cfg_sctack()
        
    def remove_item(self,channel_name):
        for mdf_index, items in enumerate(self.channel_dict_set): 
            for dict_set_cg, group_item in enumerate(items):
                try: 
                    index = list(self.cfg_sig_dict_set[mdf_index][dict_set_cg]).index(channel_name)
                except:
                    print("Delete, Key not found -> exit")
                    continue 
                    
                #cg_ch= it.child(dict_set_cg)
                it= self.treeWidget.topLevelItem(mdf_index)
                #Find index based on name
                it_items = QTreeWidgetItemIterator(it)
                index_child=0
                index=0
                channel_item_flg=False
                #TODO: Improve algorithm for indexing
                while it_items.value():
                    child_item=it_items.value()
                    if (child_item.text(0).find("Channel group")!= -1):
                        index_child=0
                        channel_item_flg=True
                    elif channel_item_flg:
                        index_child+=1
                        tmp=child_item.text(0)
                        if child_item.text(0) == channel_name:
                            index=index_child-1
                            break
                
                    it_items += 1 
                
                cg_ch = it.child(dict_set_cg)
                ch_it= cg_ch.child(index)
                        
                it.removeChild(ch_it)
                
                (self.keys_cfg_set[mdf_index][dict_set_cg]).pop(index)
                (self.values_cfg_set[mdf_index][dict_set_cg]).pop(index)
                #yml
                (self.keys_cfg_set_yml[mdf_index][dict_set_cg]).pop(index)
                (self.values_cfg_set_yml[mdf_index][dict_set_cg]).pop(index)
                del (self.cfg_sig_dict_set[mdf_index][dict_set_cg])[channel_name]
                del (self.cfg_sig_dict_set_yml[mdf_index][dict_set_cg])[channel_name] 
        return        
    
    def update_rules(self):
        #Update the selection rules
            merge_selected_sig={}
            for i in range (len(self.cfg_sig_dict_set_yml)):
                for obj in self.cfg_sig_dict_set_yml[i]:
                    merge_selected_sig.update(obj)
            
            self.selected_signals_yml=copy.deepcopy(merge_selected_sig) 
            return      
              
    def init_cfg_data_set(self):
        #Initialises the configured signals structure
        group_itmes_set=[]
        key_item_set=[]
        value_item_set=[]
        group_itmes_set_yml=[]
        key_item_set_yml=[]
        value_item_set_yml=[]
        
        if  not self.cfg_sig_dict_set:
            self.cfg_sig_dict ={}
            self.cfg_sig_dict_yml =[]
            for mdf_index, items in enumerate(self.channel_dict_set):
                group_itmes_set=[]
                if self.selected_signals_yml is not None:
                    for group_itmes in items:
                        self.keys_cfg=[]
                        self.values_cfg=[]
                        self.keys_cfg_yml=[]
                        self.values_cfg_yml=[]
                        for sig_val_index, sig_val in enumerate(group_itmes.values()):
                            for key_index, value in enumerate(self.selected_signals_yml.values()):
                                #Accessing dictionary value by index
                                if list(group_itmes.values())[sig_val_index] in value:
                                    self.keys_cfg.append(list(self.selected_signals_yml)[key_index])
                                    y_value=self.mdf_ch_set[mdf_index].get_channel_data(value)  
                                    #self.values_cfg.append(value)
                                    self.values_cfg.append(y_value) 
                                    self.keys_cfg_yml.append(list(self.selected_signals_yml)[key_index])  
                                    self.values_cfg_yml.append(value) 
                        
                        key_item_set.append(self.keys_cfg)
                        value_item_set.append(self.values_cfg) 
                        self.cfg_sig_dict={self.keys_cfg[index]: self.values_cfg[index] for index in range(len(self.keys_cfg))}
                        group_itmes_set.append(self.cfg_sig_dict)
                        #yml
                        key_item_set_yml.append(self.keys_cfg_yml)
                        value_item_set_yml.append(self.values_cfg_yml) 
                        self.cfg_sig_dict_yml={self.keys_cfg_yml[index]: self.values_cfg_yml[index] for index in range(len(self.keys_cfg_yml))}
                        group_itmes_set_yml.append(self.cfg_sig_dict_yml)        
                else:
                    for group_itmes in items:
                        self.keys_cfg=[]
                        self.values_cfg=[]
                        self.keys_cfg_yml=[]
                        self.values_cfg_yml=[]   
                        key_item_set.append(self.keys_cfg)
                        value_item_set.append(self.values_cfg) 
                        self.cfg_sig_dict={}
                        group_itmes_set.append(self.cfg_sig_dict)
                        #yml
                        key_item_set_yml.append(self.keys_cfg_yml)
                        value_item_set_yml.append(self.values_cfg_yml) 
                        self.cfg_sig_dict_yml={}
                        group_itmes_set_yml.append(self.cfg_sig_dict_yml)
                    
                    group_itmes_set.append(self.cfg_sig_dict)
                    key_item_set.append(self.keys_cfg)
                    value_item_set.append(self.values_cfg)
                    #yml
                    group_itmes_set_yml.append(self.cfg_sig_dict_yml)
                    key_item_set_yml.append(self.keys_cfg_yml)
                    value_item_set_yml.append(self.values_cfg_yml) 
                   
                                
                self.cfg_sig_dict_set.append(group_itmes_set)  
                self.keys_cfg_set.append(key_item_set)
                self.values_cfg_set.append(value_item_set)
                #yml
                self.cfg_sig_dict_set_yml.append(group_itmes_set_yml)
                self.keys_cfg_set_yml.append(key_item_set_yml)
                self.values_cfg_set_yml.append(value_item_set_yml)  
                   
        elif ((len(self.cfg_sig_dict_set) != len(self.channel_dict_set))):        
            index=len(self.cfg_sig_dict_set)
            self.cfg_sig_dict ={}
            self.cfg_sig_dict_yml =[]
            
            for mdf_index, group_itmes in enumerate(self.channel_dict_set[index]):
                if self.selected_signals_yml is not None:
                    self.keys_cfg=[]
                    self.values_cfg=[]
                    self.keys_cfg_yml=[]
                    self.values_cfg_yml=[]
                    for sig_val_index, sig_val in enumerate(group_itmes.values()):
                        for key_index, value in enumerate(self.selected_signals_yml.values()):
                            #Accessing dictionary value by index
                            if list(group_itmes.values())[sig_val_index] in value:
                                self.keys_cfg.append(list(self.selected_signals_yml)[key_index])
                                y_value=self.mdf_ch_set[mdf_index].get_channel_data(value)  
                                #self.values_cfg.append(value)
                                self.values_cfg.append(y_value) 
                                self.keys_cfg_yml.append(list(self.selected_signals_yml)[key_index])  
                                self.values_cfg_yml.append(value) 
                    
                    key_item_set.append(self.keys_cfg)
                    value_item_set.append(self.values_cfg) 
                    self.cfg_sig_dict={self.keys_cfg[index]: self.values_cfg[index] for index in range(len(self.keys_cfg))}
                    group_itmes_set.append(self.cfg_sig_dict)
                    #yml
                    key_item_set_yml.append(self.keys_cfg_yml)
                    value_item_set_yml.append(self.values_cfg_yml) 
                    self.cfg_sig_dict_yml={self.keys_cfg_yml[index]: self.values_cfg_yml[index] for index in range(len(self.keys_cfg_yml))}
                    group_itmes_set_yml.append(self.cfg_sig_dict_yml) 
                else: 
                    self.keys_cfg=[]
                    self.values_cfg=[]
                    self.keys_cfg_yml=[]
                    self.values_cfg_yml=[]  
                    key_item_set.append(self.keys_cfg)
                    value_item_set.append(self.values_cfg) 
                    self.cfg_sig_dict={}
                    group_itmes_set.append(self.cfg_sig_dict)
                    #yml
                    key_item_set_yml.append(self.keys_cfg_yml)
                    value_item_set_yml.append(self.values_cfg_yml) 
                    self.cfg_sig_dict_yml={}
                    group_itmes_set_yml.append(self.cfg_sig_dict_yml)
                    
                    group_itmes_set.append(self.cfg_sig_dict)
                    key_item_set.append(self.keys_cfg)
                    value_item_set.append(self.values_cfg)
                    #yml
                    group_itmes_set_yml.append(self.cfg_sig_dict_yml)
                    key_item_set_yml.append(self.keys_cfg_yml)
                    value_item_set_yml.append(self.values_cfg_yml)         
            
            self.cfg_sig_dict_set.append(group_itmes_set)
            self.keys_cfg_set.append(key_item_set)
            self.values_cfg_set.append(value_item_set)
            #yml
            self.cfg_sig_dict_set_yml.append(group_itmes_set_yml)
            self.keys_cfg_set_yml.append(key_item_set_yml)
            self.values_cfg_set_yml.append(value_item_set_yml)
        return
    
    def fill_tbl_cfg(self):
            tbl_row=0
            index=self.ui.listMdf.currentRow()
            cg_index=self.ui.listCg.currentRow()    
            tbl_row=len(self.tbl_channel_dict_set[index][cg_index])
            self.ui.tableChannels.setRowCount(tbl_row)
            self.ui.tableChannels.setColumnCount(3)
            self.ui.tableChannels.setHorizontalHeaderLabels(["All","Channel","Channel path"])
            self.ui.tableChannels.setColumnWidth(0, 100)
            self.ui.tableChannels.setColumnWidth(1, 200)
            self.ui.tableChannels.setColumnWidth(2, 1500)
             
            i=0
            checked_sig=[]
            while i < tbl_row:
                chkBoxItem = QTableWidgetItem()
                chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                
                for j in range(len(self.cfg_sig_dict_set[index][cg_index])):
                    sig_cfg=list(self.cfg_sig_dict_set[index][cg_index].items())[j][0]
                    sig_src=list(self.tbl_channel_dict_set[index][cg_index].items())[i][0]
                    #Check if already checked
                    if ((sig_cfg==sig_src) and not any(sig_cfg in word for word in checked_sig) or self.all_sig_sel):
                        chkBoxItem.setCheckState(Qt.Checked)
                        checked_sig.append(sig_cfg)
                        break   
                else:
                    chkBoxItem.setCheckState(Qt.Unchecked)
                
                if i !=0:
                    self.ui.tableChannels.setItem(i, 0, QTableWidgetItem(chkBoxItem))
                    self.ui.tableChannels.setItem(i, 1, QTableWidgetItem(list(self.tbl_channel_dict_set[index][cg_index].items())[i][0]))
                    self.ui.tableChannels.setItem(i, 2, QTableWidgetItem(list(self.tbl_channel_dict_set[index][cg_index].items())[i][1]))
                else:
                    #Prohibit the change of the time based channel name
                    self.ui.tableChannels.setItem(i, 0, QTableWidgetItem(chkBoxItem))
                    channel_item=QTableWidgetItem(list(self.tbl_channel_dict_set[index][cg_index].items())[i][0])
                    channel_item.setFlags(channel_item.flags() ^ Qt.ItemIsEditable)
                    self.ui.tableChannels.setItem(i, 1, channel_item)
                    channel_path_item=(QTableWidgetItem(list(self.tbl_channel_dict_set[index][cg_index].items())[i][1]))
                    channel_path_item.setFlags(channel_path_item.flags() ^ Qt.ItemIsEditable)
                    self.ui.tableChannels.setItem(i, 2, channel_path_item )  
                i+=1      
    
    def apply_cfg(self):
            self.clear()
            #self.config_ch_yaml()
            appearance=0
        
            if (self.ui.listMdf.count() !=0):
                dict_set=self.ui.listMdf.currentRow()
                dict_set_cg=self.ui.listCg.currentRow()
                it = self.treeWidget.topLevelItem((self.ui.listMdf.currentRow())) 
                tbl_max_times= self.ui.tableChannels.rowCount()
                
                #Store the items form table to the list
                tbl_item_list=[]
                for index in range(self.ui.tableChannels.rowCount()):
                    if self.ui.dict_All_Sig_Sel.isChecked():
                        #For now there is no option to save selected channels as all channels are selected
                       return 
                    elif (self.ui.tableChannels.item(index,1).text().strip()):
                            tbl_item_list.append(self.ui.tableChannels.item(index,1).text())
                            appearance=tbl_item_list.count(tbl_item_list[index])
                            #Apply only if the signal is defined once
                            item_state=self.ui.tableChannels.item(index,0).checkState()== Qt.Checked
                            if appearance<2:
                                new_value=self.ui.tableChannels.item(index,0).text()
                                current_item=list(self.channel_dict_set[self.ui.listMdf.currentRow()][dict_set_cg].items())[index][0]
                                new_item=self.ui.tableChannels.item(index,1).text()
                                #Propagate new channel names into the tree view
                                uid_channel_id=current_item+str(self.ui.listMdf.currentRow())
                                if (current_item != new_item and item_state ):
                                    #If the channel name was changed and it was previously plotted, remove  the signal from vb
                                    for i, obj in enumerate(self.req_channels): 
                                        if obj == uid_channel_id:
                                            self.legend.removeItem(self.plots_obj[i].name())
                                            #delete specific ploted curve + vb 
                                            self.p1.vb.removeItem(self.plots_obj[i]) 
                                            self.req_channels.remove(uid_channel_id)
                                            self.plots_obj.remove(self.plots_obj[i])
                                            self.ViewBoxes.remove(self.ViewBoxes[i])
                                            self.plots.pop(i) 
                                    try:        
                                        cfg_index=list(self.cfg_sig_dict_set[dict_set][dict_set_cg]).index(current_item)  
                                    except:
                                        print("Element is not in the configuration yet!")
                                        return
                                    
                                    #Rename Key in dictionary
                                    self.cfg_sig_dict_set[dict_set][dict_set_cg]= {new_item if k == current_item else k:v for k,v in self.cfg_sig_dict_set[dict_set][dict_set_cg].items()}   
                                    self.cfg_sig_dict_set_yml[dict_set][dict_set_cg]= {new_item if k == current_item else k:v for k,v in self.cfg_sig_dict_set_yml[dict_set][dict_set_cg].items()}   
                                    cg_ch= it.child(dict_set_cg)
                                    ch_it= cg_ch.child(cfg_index)
                                    ch_it.setData(0,0,str(new_item)) 
                                    
                                elif (current_item != new_item and not item_state):
                                    tbl_item_list[index]=current_item  
                            else:
                                self.reinit_tbl() 
                                chkBoxItem = QTableWidgetItem()
                                chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                                chkBoxItem.setCheckState(Qt.Unchecked)
                                print(str(index))
                                tbl_index=index
                                self.ui.tableChannels.setItem(tbl_index, 0, QTableWidgetItem(chkBoxItem))
                                dialog = QMessageBox(self.centralwidget) 
                                dialog.setText("The channel name appears more than once! The changed name is set back")
                                dialog.setFont(QFont('Arial', 15))
                                dialog.setStandardButtons(QMessageBox.StandardButton.Close)
                                dialog.show() 
                                return                                    
                    else:
                        self.reinit_tbl()        
                        dialog = QMessageBox(self.centralwidget) 
                        dialog.setText("The channel name is empty! The changed name is set back")
                        dialog.setFont(QFont('Arial', 15))
                        dialog.setStandardButtons(QMessageBox.StandardButton.Close)
                        dialog.show()
                        continue                          
            else:
                return
        
            final_dict = dict(zip(tbl_item_list, list(self.channel_dict_set[dict_set][dict_set_cg].values())))
            self.channel_dict_set[dict_set][dict_set_cg]=final_dict
            self.tbl_channel_dict_set= copy.deepcopy(self.channel_dict_set)
            self.cfg_window.close()
            self.cfg_window=None
            self.write_yaml()
            return       
            
    def cfg_closeEvent(self):
        self.cfg_window=None     
    
    def update_conf_cg_list(self):
        self.ui.listCg.clear()
        index=self.ui.listMdf.currentRow()
        for i in range (len(self.mdf_cg_set[index])):
            self.ui.listCg.insertItem(i, self.mdf_cg_set[index][i])
            
        self.ui.listCg.setCurrentRow(0)
        self.fill_tbl_cfg()

# Calculate Integration          
    def sig_integration(self):
        if self.sig_integ_window is None:
            self.sig_integ_window = Sig_Integration(self)
        else:
            return    
        self.ui = Ui_Sig_Integration()
        self.ui.setupUi(self.sig_integ_window)
        self.sig_integ_window.closed.connect(self.sig_integ_closeEvent)
        
        for i in range (len(self.mdf_toplevel_item)):
            self.ui.listMdf_SigIntg.insertItem(i, self.mdf_toplevel_item[i])
        
        for i in range (len(self.mdf_cg_set[0])):
            self.ui.listCg_SigIntg.insertItem(i, self.mdf_cg_set[0][i])
            
        self.ui.listMdf_SigIntg.itemClicked.connect(self.update_integ_list)   
        self.ui.listMdf_SigIntg.itemSelectionChanged.connect(self.update_integ_list)
        
        self.ui.listCg_SigIntg.itemClicked.connect(self.fill_tbl_integ)   
        self.ui.listCg_SigIntg.itemSelectionChanged.connect(self.fill_tbl_integ)
        
        self.ui.tableChannels_Integ.itemClicked.connect(self.table_integ_element_cnd)
       
        self.ui.listMdf_SigIntg.setCurrentRow(0)
        self.ui.listCg_SigIntg.setCurrentRow(0)
        
        self.sig_integ_window.show()
        self.sig_integ_window.setWindowTitle("Signal integration") 
        return
    
    def init_integ_data_set(self):
        #Initialises the integer calculated signal structure
        group_itmes_set=[]
        key_item_set=[]
        value_item_set=[]
        if  not self.intg_sig_dict_set:
            for items in self.channel_dict_set:
                group_itmes_set=[]
                for group_itmes in items:
                    self.intg_sig_dict =[]
                    self.keys_intg=[]
                    self.values_intg=[]
                    key_item_set.append(self.keys_intg)
                    value_item_set.append(self.values_intg)                    
                    group_itmes_set.append(self.intg_sig_dict)
                self.intg_sig_dict_set.append(group_itmes_set)    
                self.keys_intg_set.append(key_item_set)
                self.values_intg_set.append(value_item_set)       
            
        elif ((len(self.intg_sig_dict_set) != len(self.channel_dict_set))):        
            index=len(self.intg_sig_dict_set)
            for group_itmes in self.channel_dict_set[index]:
                self.intg_sig_dict =[]
                self.keys_intg=[]
                self.values_intg=[]
                group_itmes_set.append(self.intg_sig_dict)
                key_item_set.append(self.keys_intg)
                value_item_set.append(self.values_intg)
                
            self.intg_sig_dict_set.append(group_itmes_set)
            self.keys_intg_set.append(key_item_set)
            self.values_intg_set.append(value_item_set)
    
        return
    
    def table_integ_element_cnd(self, item):
        dict_set=self.ui.listMdf_SigIntg.currentRow()
        dict_set_cg=self.ui.listCg_SigIntg.currentRow()
        it = self.treeWidget.topLevelItem((self.ui.listMdf_SigIntg.currentRow())) 
        tml_max=self.ui.tableChannels_Integ.rowCount()
        cg_ch= it.child(dict_set_cg)
        ch_it= cg_ch.child(item.row())
        channel_req=self.ui.tableChannels_Integ.item(item.row(),1).text()
        channel_name = "∫_" + channel_req 
        
        if item.checkState() == Qt.Checked:
            Channel_y=self.mdf_ch_set[dict_set].get_channel_data(self.channel_dict_set[dict_set][dict_set_cg].get(channel_req))
            #Get the time base i.e. 'Periodic Task 1'
            Time_sig=self.mdf_ch_set[dict_set].get_channel_data(list(self.channel_dict_set[dict_set][dict_set_cg].items())[0][0])

            Channel_y=integrate.cumulative_trapezoid(Channel_y, Time_sig, initial=0)
            
            self.keys_intg_set[dict_set][dict_set_cg].append(channel_name)
            self.values_intg_set[dict_set][dict_set_cg].append(Channel_y)
            self.intg_sig_dict_set[dict_set][dict_set_cg] = {self.keys_intg_set[dict_set][dict_set_cg][index]: self.values_intg_set[dict_set][dict_set_cg][index] for index in range(len(self.keys_intg_set[dict_set][dict_set_cg]))}
            
            cg_ch_item=[channel_name]
            ch_item=QTreeWidgetItem(cg_ch_item)  
            cg_item=self.top_level_items[dict_set].child(dict_set_cg)
            cg_item.addChild(ch_item)
            
        elif (item.checkState() == Qt.Unchecked and any(channel_name in word for word in self.intg_sig_dict_set[dict_set][dict_set_cg])):
            index = list(self.intg_sig_dict_set[dict_set][dict_set_cg]).index(channel_name)
            cg_ch= it.child(dict_set_cg)
            ch_it= cg_ch.child(tml_max+index)
            it.removeChild(ch_it)
            (self.keys_intg_set[dict_set][dict_set_cg]).pop(index)
            (self.values_intg_set[dict_set][dict_set_cg]).pop(index)
            del (self.intg_sig_dict_set[dict_set][dict_set_cg])[channel_name] 
        else:
            return
    
    def fill_tbl_integ(self):
        tbl_row=0
        index=self.ui.listMdf_SigIntg.currentRow()
        cg_index=self.ui.listCg_SigIntg.currentRow() 
        tbl_row=len(self.tbl_channel_dict_set[index][cg_index])
        self.ui.tableChannels_Integ.setRowCount(tbl_row)
        self.ui.tableChannels_Integ.setColumnCount(2)
        self.ui.tableChannels_Integ.setHorizontalHeaderLabels(["Select","Signal"])
        self.ui.tableChannels_Integ.setColumnWidth(0, 200)
        self.ui.tableChannels_Integ.setColumnWidth(1, 1500)
        
        i=0
        checked_sig=[]
        while i < tbl_row:
            chkBoxItem = QTableWidgetItem()
            chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            
            for j in range(len(self.intg_sig_dict_set[index][cg_index])):
                sig_integ=list(self.intg_sig_dict_set[index][cg_index].items())[j][0]
                sig_src=list(self.tbl_channel_dict_set[index][cg_index].items())[i][0]
                sig_src = "∫_" + sig_src
                #Fix: The .find() replaced with '=='
                if ((sig_integ==sig_src ) and not any(sig_integ in word for word in checked_sig)):
                    chkBoxItem.setCheckState(Qt.Checked)
                    checked_sig.append(sig_integ)
                    break    
            else:
                chkBoxItem.setCheckState(Qt.Unchecked)
        
            self.ui.tableChannels_Integ.setItem(i, 0, QTableWidgetItem(chkBoxItem))
            self.ui.tableChannels_Integ.setItem(i, 1, QTableWidgetItem(list(self.tbl_channel_dict_set[index][cg_index].items())[i][0]))
            
            i+=1       
            
        return  
    
    def update_integ_list(self):
        self.ui.listCg_SigIntg.clear()
        index=self.ui.listMdf_SigIntg.currentRow()
        for i in range (len(self.mdf_cg_set[index])):
            self.ui.listCg_SigIntg.insertItem(i, self.mdf_cg_set[index][i])
            
        self.ui.listCg_SigIntg.setCurrentRow(0)
        self.fill_tbl_integ()
      
    def sig_integ_closeEvent(self):
        self.sig_integ_window=None   
               
    def splliter_moved(self):
        self.lcdNumber.setGeometry(QRect(150, 0, 100, 51))
        self.lcdNumber.display(self.text_LCD)
                 
    #Not used       
    def on_selectedchanged(self, selected, deselected):
        for ix in deselected.indexes():
            #print('Selected Cell Location Row: {0}, Column: {1}'.format(ix.row(), ix.column()))
            self.tbl_index_integ=ix.row()
            print(self.tbl_index_integ)
   
    def chk_st_All_Sig_Sel(self):
        
        if (self.ui.dict_All_Sig_Sel.isChecked()):
            if not self.all_sig_sel:
                self.remove_all_tree_items()
                self.all_sig_sel=True
                self.ui.Channel_cfg_ButtonBox.setStandardButtons(QDialogButtonBox.Cancel)
                self.add_all_sig()
                #Reset
                self.set_back_cfg_sctack()
                
                self.init_cfg_data_set()
                self.fill_tbl_cfg()
            else:
                self.all_sig_sel=False          
        else:
            self.all_sig_sel=False 
            self.ui.Channel_cfg_ButtonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
            self.remove_all_tree_items()
            
            self.load_selected_signals()
            self.init_cfg_data_set()
            self.refresh_tree_items()
            self.fill_tbl_cfg()
        
        self.config_ch_yaml()
        
    def set_full_path_dict(self):
        for mdf_dict_index, cg_set_dict in enumerate(self.channel_dict_set):
            for cg_index, cg_dict in enumerate(cg_set_dict):
                tbl_item_list=[]
                for index, key in enumerate(cg_dict):
                    value=cg_dict.get(key)
                    tbl_item_list.append(value)
                    #Update tree
                    it = self.treeWidget.topLevelItem(mdf_dict_index) 
                    cg_ch= it.child(cg_index)
                    ch_it= cg_ch.child(index)
                    ch_it.setData(0,0,str(value))
                                        
                final_dict = dict(zip(tbl_item_list, list(self.channel_dict_set[mdf_dict_index][cg_index].values())))
                self.channel_dict_set[mdf_dict_index][cg_index]=final_dict
                
    def undo_dict(self):
        
        self.channel_dict_set=[]
        
        self.channel_dict_set=copy.deepcopy(self.tbl_channel_dict_set)
        
        for i in range(len(self.mdf_ch_set)):
            ch_group_cnt=self.mdf_ch_set[i].masterChannelList
            it = self.treeWidget.topLevelItem((i))
            for ch_group_id in range (len(self.channel_dict_set[i])):
                for j in range (len(self.channel_dict_set[i][ch_group_id])):
                    list_to_string = ""
                    cg_ch_item=[list(self.channel_dict_set[i][ch_group_id].items())[j][0]]
                    for ele in cg_ch_item:
                        list_to_string += ele
                    
                    cg_ch= it.child(ch_group_id)
                    ch_it= cg_ch.child(j)
                    ch_it.setData(0,0,str(list_to_string)) 
                                                 
    def reinit_tbl(self):
        cg_index=self.ui.listMdf.currentRow()
        ch_index=self.ui.listCg.currentRow()
        tbl_row=len(self.tbl_channel_dict_set[cg_index][ch_index])
        i=0
        while i < tbl_row:
            self.ui.tableChannels.setItem(i, 1, QTableWidgetItem(list(self.tbl_channel_dict_set[cg_index][ch_index].items())[i][0]))
            i+=1  
          
    def reject(self):
        self.cfg_window.close()
        self.cfg_window=None
                          
    def help(self):
        dialog = QMessageBox(self.centralwidget) 
        dialog.setText(self.ver)
        dialog.setFont(QFont('Arial', 15))
        dialog.setStandardButtons(QMessageBox.StandardButton.Close)
        dialog.exec()
                
    def clear(self):
        self.current_ch.clear()
        it = QTreeWidgetItemIterator(self.treeWidget)
        # Set beck selected beground
        color = QBrush
        while it.value():
            node = it.value()
            node.setBackground(0,color(QColor( 255, 255, 255, 255)))
            it += 1
        self.color_cnt=0
        self.graphicsView.removeItem(self.X1_marker)
        self.graphicsView.removeItem(self.X2_marker)
        self.removecurve()
        self.plots_obj.clear()
        self.plots.clear()
        self.time_com.clear()
        self.ViewBoxes.clear()
        self.req_channels.clear()
        self.legend.clear()
        self.lcdNumber.display("0.0")     
    #Not used
    def mouse_clicked(self, mouseClickEvent):
        #Evaluation (select signal on the plot) : Not used
        # mouseClickEvent is a pyqtgraph.GraphicsScene.mouseEvents.MouseClickEvent
        print('clicked plot 0x{:x}, event: {}'.format(id(self), mouseClickEvent))
    
    def sig_man_ena(self):
        #Flag - Hold all activities as long as no MDF channels are present  
        if  ((self.treeWidget.topLevelItemCount()!=0) and (len( self.plots))!=0):
            return True
        else:
            return False   
        
    def removecurve(self):
        #delete all ploted curves
        for i, (plots, viewbox) in enumerate ( 
                zip(self.plots, self.ViewBoxes)
                ):
                    self.p1.vb.removeItem(viewbox)
                                                   
    def add_x1_cursor(self):
        if self.sig_man_ena():
            x_axis = self.graphicsView.getPlotItem().getAxis('bottom')
            xmin, xmax = x_axis.range
            x_pos_set=xmin+((xmax-xmin)/2)
            # Create the infinite (cursor) line to select an x coordinate, connect to its moved signal
            self.crosshairx = self.X1_marker
            self.crosshairx.sigPositionChanged.connect(self._crosshairx_changed)
            self.selected_x_i = 0
            self.X1_marker.setValue(x_pos_set)
            self.X1_marker.setZValue(1000)
            all_graph_items = self.graphicsView.getPlotItem().allChildItems()
            #Toggle cursor X1
            for obj in all_graph_items:
                if obj == self.X1_marker:
                    #Item was found, remove the item (Toggle the cursor)
                    self.graphicsView.removeItem(self.X1_marker)
                    return             
            #Add X1 cursor if not already added
            self.graphicsView.addItem(self.X1_marker)
        else:
            return
             
    def add_x2_cursor(self):
        try:
            [_, channel_req, mdf_set_num, is_top_level, cg_id]=self.req_curr_chann()
            #Return if top level elemment (i.e. MDF(1)) was selected
            if (is_top_level):
                return   
            if self.sig_man_ena(): 
                Channel_y2=self.y_signal_type(channel_req,mdf_set_num,cg_id) 
                #Get the time base i.e. 'Periodic Task 1'
                Time_sig= self.mdf_ch.get_channel_data(list(self.channel_dict_set[mdf_set_num][cg_id].items())[0][0])
                # Assume plot data is stored in arrays of xcoords, yvalues
                self.xcoords2 = Time_sig
                self.y2values = Channel_y2
                # Create the infinite (cursor) line to select an x coordinate, connect to its moved signal
                self.crosshairx2 = self.X2_marker
                self.crosshairx2.sigPositionChanged.connect(self._crosshairx2_changed)
                self.selected_x2_i = 0
                x_axis = self.graphicsView.getPlotItem().getAxis('bottom')
                xmin, xmax = x_axis.range
                self.X2_marker.setValue((xmax-self.crosshairx.value())/2 + self.crosshairx.value())
                self.X2_marker.setZValue(1000)
                all_graph_items = self.graphicsView.getPlotItem().allChildItems()
                #Chek for presence of X2 cursor
                for obj in all_graph_items:
                    if obj == self.X2_marker:
                        #Item was found, remove the item (Toggle the cursor)
                        self.graphicsView.removeItem(self.X2_marker)
                        return   
                #Add X2 cursor 
                self.graphicsView.addItem(self.X2_marker)     
        finally:
            return
        
    def _crosshairx_changed(self):
        # Slot to get y value of point closest to x value of the infinite line
        # Keep track of index of currently selected x coordinate, so we can avoid doing
        # unnecessary updates when the infiniteline changes but the index of the
        # closest x/y data point is still the same
        new_i = np.argmin(np.abs(self.xcoords -self.crosshairx.value()))
        if new_i !=self.selected_x_i:
            self.selected_x_i = new_i
            self.text_LCD = str(round(self.yvalues[self.selected_x_i],1))
            text = "Y1=" + self.text_LCD
            # display y axis value
            self.X1_marker_lab.setFormat(format(text))
            #LCD Disply
            self.lcdNumber.setGeometry(QRect(150, 0, 100, 51))
            self.lcdNumber.display(self.text_LCD)
            # display time in [s]
            self.text_Time.setText("t= "+str(round(self.xcoords[self.selected_x_i],2))+"s")
            self.text_Time.setAlignment(Qt.AlignRight)
            
    def _crosshairx2_changed(self):
        # Slot to get y value of point closest to x value of the infinite line
        # Keep track of index of currently selected x coordinate, so we can avoid doing
        # unnecessary updates when the infiniteline changes but the index of the
        # closest x/y data point is still the same
        new_i = np.argmin(np.abs(self.xcoords2 -self.crosshairx2.value()))
        if new_i !=self.selected_x2_i:
            self.selected_x2_i = new_i
            try:
                y2_val=str(round(self.y2values[self.selected_x2_i],3))
                if y2_val is not None:
                    text_LCD=y2_val
                else:
                    text_LCD = str(0)
            except:
                    text_LCD = str(0)
            
            diff=str(round(((self.y2values[self.selected_x2_i]))-((self.yvalues[self.selected_x_i])),3))
            text = "Y2=" + text_LCD 
            self.delta_Y.setText("ΔY= " + diff)
            self.delta_Y.setAlignment(Qt.AlignRight)  
            # display y axis value
            self.X2_marker_lab.setFormat(format(text))
            # display delta time in [s]
            self.delta_Time.setText("Δt= "+str(round(abs(self.xcoords[self.selected_x2_i]-self.xcoords[self.selected_x_i]),3))+"s")
            self.delta_Time.setAlignment(Qt.AlignRight)  
            
    def get_xy_time_common(self):
        
            start_x = np.nanmin(
                            [
                                np.nanmin(Time_sig)
                                for Time_sig in self.time_com
                                if len(self.time_com)
                            ]
                        )
            stop_x = np.nanmax(
                            [
                                np.nanmax(Time_sig)
                                for Time_sig in self.time_com
                                if len(self.time_com)
                            ]
                        )
             
            start_y = np.nanmin(
                            [
                                np.nanmin(plots)
                                for plots in self.plots
                                if len(self.plots)
                            ]
                        )
            
            stop_y = np.nanmax(
                            [
                                np.nanmax(plots)
                                for plots in self.plots
                                if len(self.plots)
                            ]
                        )
            return start_x, stop_x, start_y, stop_y
          
    def fit_plot_xy(self):
        #resize all curves to start position
        self.x_range_hold()
        if self.sig_man_ena():
            [start_ts, stop_ts, _, _]= self.get_xy_time_common()
            #scale all on Y axis to the last active plot
            for i, viewbox in enumerate(self.ViewBoxes):
                start_y = np.nanmin(self.plots[i])
                stop_y = np.nanmax(self.plots[i])
                viewbox.setXRange(start_ts, stop_ts) 
                viewbox.setYRange(start_y, stop_y) 
              
        else:
            return   
        
    def stack_all(self):
        #stack all curves 
        self.x_range_hold()
        if self.sig_man_ena():
            [start_ts, stop_ts, _, _]= self.get_xy_time_common()
            count=len(self.ViewBoxes)
             
            for position, viewbox in enumerate(self.ViewBoxes):
                min_ = np.nanmin(self.plots[position])
                max_ = np.nanmax(self.plots[position])
                
                #algorithm taken over form asammdfgui 
                dim = (float(max_) - min_) * 1.1
                max_ = min_ + dim * count - 0.05 * dim
                min_ = min_ - 0.05 * dim
                
                min_, max_ = (
                                min_ - dim * position,
                                max_ - dim * position,
                            ) 
                viewbox.setXRange(start_ts, stop_ts) 
                viewbox.setYRange(min_, max_)
                   
        else:
            return
        
    def scale_y(self):
        #resize all curves to start position
        self.x_range_hold()
        if self.sig_man_ena():
            [start_ts, stop_ts, start_y, stop_y]= self.get_xy_time_common()
            #scale all on Y axis
            for i, viewbox in enumerate(self.ViewBoxes):
                viewbox.setXRange(start_ts, stop_ts) 
                viewbox.setYRange(start_y, stop_y)
        else:
            return   
            
    def x_range_hold(self):
        # hold actual zoomed range of viewbox in start_x, stop_x
        ( self.start_x, self.stop_x), _ = self.p1.vb.viewRange()   
    
    def get_mdf_creation_date(self):
        current_id = self.treeWidget.currentItem()
        top_level_id =self.treeWidget.indexOfTopLevelItem(current_id)
        #Ask if not top levle item
        if (top_level_id==-1):
            item =current_id.parent()
            top_level_id=self.treeWidget.indexOfTopLevelItem(item) 
            
        date_mdf = os.path.getctime(self.mdf_file_in_set[top_level_id])
        full_name = os.path.basename(self.mdf_file_in_set[top_level_id])
        file_name = os.path.splitext(full_name)
        date_mdf_format =datetime.fromtimestamp(date_mdf).strftime("%d/%m/%Y, %H:%M:%S")
        current_id.setToolTip(0, date_mdf_format + ' ' + file_name[0])      
      
    def change_signal_focus(self):
        self.hold_view
        [current_id, channel_req, mdf_set_num, is_top_level, cg_id]=self.req_curr_chann()
        #Return if top level elemment selected
        if (is_top_level):
            return
        #Make unique channel    
        uid_channel_id=channel_req+str(mdf_set_num)
        
        channel_req_name = channel_req + ' (' + str(mdf_set_num + 1) + ')'
        #self.current_ch.setText(channel_req_name + "=")
        self.current_ch.setHtml(
            "<b>"+channel_req_name + "="+ "</b>"
        )
             
        for i, obj in enumerate(self.req_channels): 
            if obj == uid_channel_id:
                [_, _, start_y, stop_y]= self.get_xy_time_common()               
                self.p1.getAxis('left').linkToView(self.ViewBoxes[i])
                self.ViewBoxes[i].setXRange(self.start_x, self.stop_x) 
                self.ViewBoxes[i].setYRange(start_y, stop_y) 
                self.p1.scene().setFocusItem(self.ViewBoxes[i]) 
        return  
      
    def remove_plotted_sig(self,channel_req,mdf_set_num,current_id):
        #def unique id
        uid_channel_id=channel_req+str(mdf_set_num)
        # Set back highlight of current item
        current_id.setBackground(0,QBrush(QColor( 255, 255, 255, 255)))
        
        for i, obj in enumerate(self.req_channels): 
            if obj == uid_channel_id:
                print("already ploted, remove signal")
                self.legend.removeItem(self.plots_obj[i].name())
                #delete specific ploted curve + vb 
                self.p1.vb.removeItem(self.plots_obj[i]) 
                self.req_channels.remove(uid_channel_id)
                self.plots_obj.remove(self.plots_obj[i])
                self.ViewBoxes.remove(self.ViewBoxes[i])
                self.plots.pop(i) 
        return  
    
    def tree_element_dbclick(self):
        [current_id, channel_req, mdf_set_num, is_top_level, cg_id]=self.req_curr_chann()
        #Return if top level elemment selected
        if (is_top_level):
            return
        
        self.remove_plotted_sig(channel_req,mdf_set_num,current_id)
        
        return
            
    def req_curr_chann(self):
        is_top_level=False
        #Current cliked/selected item in tree
        #Issue 1: if an tree element is clicked again the selectedIndexes is not providing info  
        current_id = self.treeWidget.currentItem()
        top_level_id =self.treeWidget.indexOfTopLevelItem(current_id)   
       
        for ix in self.treeWidget.selectedIndexes():
            channel_req = ix.data(Qt.DisplayRole)  
            
        #If top level element slected ->exit
        if (top_level_id>-1) or (channel_req.find("Channel group") != -1):
            is_top_level=True
            current_id=0
            channel_req=0
            mdf_set_num=0
            cg_id = 0
            return current_id, channel_req, mdf_set_num, is_top_level, cg_id
        
        # Get the top level item 
        cg_item=current_id.parent()
        item=cg_item.parent()
        cg_id=item.indexOfChild(cg_item)
        # Get the topl level item index 0....x
        mdf_set_num=self.treeWidget.indexOfTopLevelItem(item)  
        
        return current_id, channel_req, mdf_set_num, is_top_level, cg_id
    
    def y_signal_type(self,channel_req,mdf_set_num,cg_id):
        #Chek if calculated signal is selected    
        if (channel_req.find("∫") != -1):
            Channel_y=self.intg_sig_dict_set[mdf_set_num][cg_id].get(channel_req)
        else:
            Channel_y=self.mdf_ch_set[mdf_set_num].get_channel_data(self.channel_dict_set[mdf_set_num][cg_id].get(channel_req))
        return Channel_y
                        
    def tree_element_click(self):   
        [current_id, channel_req, mdf_set_num, is_top_level, cg_id]=self.req_curr_chann()
         #Return if top level elemment selected
        if (is_top_level):
            return
        
        Channel_y=self.y_signal_type(channel_req,mdf_set_num,cg_id)   
        #Get the time base i.e. 'Periodic Task 1'
        Time_sig=self.mdf_ch_set[mdf_set_num].get_channel_data(list(self.channel_dict_set[mdf_set_num][cg_id].items())[0][0])
        #Assume plot data is stored in arrays of xcoords, yvalues
        self.xcoords = Time_sig
        self.yvalues = Channel_y
       
        self.plot_signal_vb(Time_sig,Channel_y,channel_req,mdf_set_num, current_id)
        return
          
    def hold_view(self):
        #Hold initial view box size
        Time_sig=self.mdf_ch_set[0].get_channel_data(list(self.channel_dict.items())[0][0])
        start_ts = np.amin(Time_sig)
        stop_ts = np.amax(Time_sig)
        self.graphicsView.setXRange(start_ts, stop_ts)
        self.x_range_hold()
              
    def updateViews(self):
        #View has resized; update auxiliary views to match 
        for viewbox in  self.ViewBoxes:
                    viewbox.setGeometry(self.p1.getViewBox().sceneBoundingRect())
    
    def file_open(self):    
        # Import MDF file over Menu (File/Open)
        try:
            mdf_file, _= QFileDialog.getOpenFileName()
            if(self.insert_mdf_ch(mdf_file)):
                self.ena_act_menu()
                self.init_integ_data_set()
                self.init_cfg_data_set()
                #Hold view box size after the first MDF import   
                if (self.treeWidget.topLevelItemCount()<2):
                    self.hold_view()  
            else:
                return              
        except:
            print("Error importing Mdf")
            return
        
    def create_mdf_dict(self, arg, mdf_set_num, cg_index):
        all_channels = []
        channel_dict = [] 
        for index, group in enumerate(arg):
            #Skip the first channel: Time based channel i.e. Periodic Task 1
            if (index!=0):
                #Filter for IO Signals
                if(chennel_type(group) != 0):
                    all_channels.append(group)
                    values.append(all_channels[index])
                    keys.append(extract_channel_name(all_channels[index],channel_dict,index, mdf_set_num, cg_index))
                    channel_dict = {keys[index]: values[index] for index in range(len(keys))}  
                else:
                    all_channels.append(group)
                    values.append(all_channels[index])
                    keys.append(extract_non_IO_channel_name(all_channels[index],channel_dict,index, mdf_set_num, cg_index))
                    channel_dict = {keys[index]: values[index] for index in range(len(keys))}
                    continue
            else:
                all_channels.append(group) 
                keys=[all_channels[0]]
                values=[all_channels[0]]
                
        comp_channel_dict = copy.deepcopy(channel_dict)
        return channel_dict, comp_channel_dict  
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # Import MDF file over drag and drop over the list widget box
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    mdf_file = str(url.toLocalFile())
                    
            if(self.insert_mdf_ch(mdf_file)):
                self.ena_act_menu()
                self.init_integ_data_set()
                self.init_cfg_data_set()
            #Hold view box size after the first MDF import   
                if (self.treeWidget.topLevelItemCount()<2):
                    self.hold_view()  
            else:
                return
        else:
            event.ignore()
    
    def get_cg_name(self,index,arg):
        dict_cg=list(mdfreader.MdfInfo(arg).items())[5][1][index][0].get('Comment')
        cg_name=dict_cg.get('Comment')
        if cg_name is None:
            dict_cg=list(mdfreader.MdfInfo(arg).items())[5][1][index][0].get('acq_name')
            cg_name=dict_cg.get('Comment')
        return cg_name
             
    def insert_mdf_ch(self,arg):
        if arg.endswith('.mf4'):
            
            self.mdf_file_in_set.append(arg)
            mdf_set_num=len(self.mdf_file_in_set)
           
            self.mdf_ch = mdfreader.Mdf(arg)
            self.mdf_ch_set.append(self.mdf_ch)
            #Number of channles 
            ch_group_cnt=self.mdf_ch.masterChannelList
            channel_dict_group_set = []
            tbl_channel_dict_set = []
            tbl_channel_dict=[]
            for cg_index, ch_group_id in enumerate(range (len(ch_group_cnt))):
                [self.channel_dict, tbl_channel_dict] = self.create_mdf_dict(list(ch_group_cnt.items())[ch_group_id][1], mdf_set_num, cg_index)
                channel_dict_group_set.append(self.channel_dict)
                tbl_channel_dict_set.append(tbl_channel_dict)
                
            self.channel_dict_set.append(channel_dict_group_set)                         
            self.tbl_channel_dict_set.append(tbl_channel_dict_set)        
            #Add title to the top level item MDF (x)
            mdf_item=QTreeWidgetItem(self.treeWidget)
            mdf_toplevel_item_name='MDF'+' ('+str(mdf_set_num)+ ')' 
            self.mdf_toplevel_item.append(mdf_toplevel_item_name)
            mdf_item.setText(0,mdf_toplevel_item_name)
            
            self.top_level_items.append(mdf_item)
            ch_cg_index=len(self.channel_dict_set[mdf_set_num-1])
            cg_item_id=mdf_set_num-1
            cg_set=[]
            for i in range(ch_cg_index):
                try:
                    cg_name="(" + self.get_cg_name(i,arg) + ")"
                except:
                    cg_name =" "
                        
                cg_item_name = "Channel group" + " " + str(i) + " " + cg_name
                cg_item=QTreeWidgetItem([cg_item_name])
                cg_set.append(cg_item_name)
                self.top_level_items[cg_item_id].addChild(cg_item)
                
                #Add switch to enable adding all signals
                if (self.all_sig_sel):
                    for j in range (len(self.channel_dict_set[cg_item_id][i])):
                        cg_ch_item=[list(self.channel_dict_set[cg_item_id][i].items())[j][0]]
                        ch_item=QTreeWidgetItem(cg_ch_item)  
                        cg_item=self.top_level_items[cg_item_id].child(i)
                        cg_item.addChild(ch_item)
                    
                    #Add all signals to the selection rules
                    merge_selected_sig={}
                    for i in range (len(self.channel_dict_set)):
                        for obj in self.channel_dict_set[i]:
                            merge_selected_sig.update(obj)
            
                    self.selected_signals_yml=copy.deepcopy(merge_selected_sig)  
                    #Test
                else:
                    self.insert_sig_tree(cg_item_id,i)
                        
            self.mdf_cg_set.append(cg_set)  
            
            
        elif (not (arg and arg.strip())):
            return False
        else:
            dialog = QMessageBox(self.centralwidget) 
            dialog.setText("Wrong (non-MDF) file format!")
            dialog.setFont(QFont('Arial', 15))
            dialog.setStandardButtons(QMessageBox.StandardButton.Close)
            dialog.show()   
            return False
        
        return True
    
    def add_all_sig(self):  
        for cg_item_id, items in enumerate(self.channel_dict_set): 
            for dict_set_cg, group_item in enumerate(items):
                for j in range (len(self.channel_dict_set[cg_item_id][dict_set_cg])):
                    cg_ch_item=[list(self.channel_dict_set[cg_item_id][dict_set_cg].items())[j][0]]
                    ch_item=QTreeWidgetItem(cg_ch_item)  
                    cg_item=self.top_level_items[cg_item_id].child(dict_set_cg)
                    cg_item.addChild(ch_item)
            
        #Add all signals to the selection rules
        merge_selected_sig={}
        for i in range (len(self.channel_dict_set)):
            for obj in self.channel_dict_set[i]:
                merge_selected_sig.update(obj)
    
        self.selected_signals_yml=copy.deepcopy(merge_selected_sig)  
        return
    
    def insert_sig_tree(self,cg_item_id,i):
        for j in range (len(self.channel_dict_set[cg_item_id][i])):
            search=list(self.channel_dict_set[cg_item_id][i].items())[j][1]
            current_item=list(self.channel_dict_set[cg_item_id][i].items())[j][0]
            if self.selected_signals_yml is None:
                return
            for key_index, value in enumerate(self.selected_signals_yml.values()):
                #Search if a signal name is defined for the signal path in the yaml configuration file
                if search in value:
                    cg_ch_item=[list(self.selected_signals_yml)[key_index]]
                    ch_item=QTreeWidgetItem(cg_ch_item)  
                    cg_item=self.top_level_items[cg_item_id].child(i)
                    cg_item.addChild(ch_item)
                    current_item=str(list(self.channel_dict_set[cg_item_id][i])[j])
                    new_item=str(list(self.selected_signals_yml)[key_index])
                    self.channel_dict_set[cg_item_id][i]= {new_item if k == current_item else k:v for k,v in self.channel_dict_set[cg_item_id][i].items()}
                    tmo2=2
                       
        self.tbl_channel_dict_set= copy.deepcopy(self.channel_dict_set)
        return
                          
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def closeEvent(self, event):
        try:
            self.cfg_window.close()
        except:
            print("Exit Issue !")
            
        #Close all main windows
        #for window in QApplication.topLevelWidgets():
        #    window.close()
           
        #sys.exit(0)
        return
               
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    ui=MainWindow()
  
    ui.show()
    
    sys.exit(app.exec())