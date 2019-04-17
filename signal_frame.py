from signaldef import *
from parsexml import *

sig_obj1 = SignalDefinition(name="Temperature_Bosch", minimum="-40.15", maximum="130.10",
                                                   unit="°C", default="25.99", frame_number='1',
                                                   physical=Physical(x1=-40.15, x2=130.10, y1=264, y2=1626,
                                                                     bitwidth=12, format='.3f'))
sig_obj2 = SignalDefinition(name="Differential Air Pressure", minimum="-16", maximum="2",
                                                   unit="KiloPascal", default="-17.99876543", frame_number='1',
                                                   physical=Physical(x1=-16, x2=2, y1=193, y2=3896, bitwidth=12, format='.2f'))

def valid_frames_from_xml():
    xml_file_path = os.path.join(os.getcwd(), "signaldefinition.xml")
    sig_conf = read_sigdef(xml_file_path)
    frames = []
    for fc in range(16):
        frame = get_sig_by_fc(sig_conf, fc)
        if frame:
            frames.append(frame)
    return frames


def signal_details_from_frames():
    signal_details = []
    signal_frames = valid_frames_from_xml()
    for sigs in signal_frames:
        if len(sigs) > 1:
            signal_details.append((sigs[0].get_signal_details(), sigs[1].get_signal_details()))
        else:
            signal_details.append((sigs[0].get_signal_details(), None))
    return signal_details


class SignalFrame(Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.sigrows = []


        # TODO: do not create rows here, use separate method "add_row"
        # TODO: do not use SignalDefinition objects but signal_details
        # row = SignalRow(self, row=2,
        #                 signal_details=(sig_obj1.get_signal_details(), sig_obj2.get_signal_details()))
        #
        # self.sigrows.append(row)
        for signal_details in signal_details_from_frames():
            self.add_signal_row((len(self.sigrows) + 1) * 2, signal_details)

        self.row_position = (len(self.sigrows) + 1) * 2

        self.create_label_bitfield()
        self.create_entry_bitfield()
        self.chunks_bitfield(16, 4)
        self._create_button_widget()
        self._create_column_heading_signal_name(heading_text="Signal Name 1", column=0)
        self._create_column_heading_signal_name(heading_text="Signal Name 2", column=3)
        self._create_column_heading_signal_widgets()

    def commit(self, dummy=None):
        for row_obj in self.sigrows:
            row_obj.commit()

    def add_signal_row(self, row_pos, signal_details):
            sigrow = SignalRow(self, row=row_pos, signal_details=signal_details)
            self.sigrows.append(sigrow)

    def create_chkbtns_bitfield(self, row, row_chunk_size, count):
        for col in range(row_chunk_size):
            #count += col
            chkbtn_bitfield = Checkbutton(self, text="Bit_{}".format(col+count), variable=bitfield_indicator)
            chkbtn_bitfield.grid(row=row, column=col+6)

    def chunks_bitfield(self, bitwidth, row_div):
        chunk_size = int(bitwidth / row_div)
        for row_num in range(chunk_size):
            bit_count = chunk_size * row_num
            self.create_chkbtns_bitfield(self.row_position+row_num, chunk_size, bit_count)

    def create_label_bitfield(self):
        bitfield_label = Label(self, text="Bitfield Label Demo !!!", font=("Helvetica", 12))
        bitfield_label.grid(row=self.row_position+1, column=0, columnspan=3, sticky=W+E)

    def create_entry_bitfield(self):
        entry_default = StringVar()
        bitfield_entry = Entry(self, textvariable=entry_default, width=28)
        bitfield_entry.grid(row=self.row_position+1, column=4)

    def _create_button_widget(self):
        self.b_update = Button(self, text="Update", command=self.commit, state=NORMAL)
        self.b_update.grid(row=7, column=12, sticky='NE', padx=7)

    def get_values(self):
        lst = [row_obj.get_user_value() for row_obj in self.sigrows]
        print(lst)
        return lst

    def _create_column_heading_signal_name(self, heading_text, column):
        """
        Create the Heading of column to display the name of signal 1 & 2.

        Subheadings will be displayed into individual column by spanning the main column.

        By default signal Name heading will be created on row position 0 & subheadings on row position 1.

        To get the actual signal row, user should start the row from position 2.
        Args:
            master = Main tkinter frame
            heading_text = given name for signal 1 & 2 during method call.
            column = given column number during method call.
        """
        subheadings = ["Minimum", "Maximum", "Unit"]
        lbl_column_signame = Label(self, text=heading_text, bg=COLUMN_COLOR_LIST[column], font='Helvetica 11 bold')
        lbl_column_signame.grid(row=0, column=column, columnspan=len(subheadings), sticky=W + E)
        for index, element in enumerate(subheadings):
            lbl = Label(self, text=element, bg=COLUMN_COLOR_LIST[column], font='Helvetica 9 bold')
            lbl.grid(row=1, column=column + index, sticky=W + E)

    def _create_column_heading_signal_widgets(self):
        """
        Create the heading of column to display the respective widgets for signal 1 & 2 and also to display the headings of
        the common widgets, which is applicable for both signal 1 & 2.
        Args:
            master = Main tkinter frame
        """
        column_headings_sig_widgets = ["Measured Value 1", "User Value 1", "Measured Value 2", "User Value 2",
                                       "Gateway", "Signal Active"]
        start_index = 6
        for col, label in enumerate(column_headings_sig_widgets, start_index):
            heading_sig_widgets = Label(self, text=label, bg=COLUMN_COLOR_LIST[col], font='Helvetica 11 bold')
            empty_lbl = Label(self, text="", bg=COLUMN_COLOR_LIST[col], width=24)
            heading_sig_widgets.grid(row=0, column=col, sticky=W + E)
            empty_lbl.grid(row=1, column=col)

if __name__ == '__main__':
    root = Tk()
    sigframe = SignalFrame(master=root)
    sigframe.grid()
    root.mainloop()
    #print(signal_details_from_frames())