from enum import Enum
from tkinter import *

COLUMN_COLOR_LIST = [
    '#8EE5EE',
    '#8EE5EE',
    '#8EE5EE',
    '#C1CDCD',
    '#C1CDCD',
    '#C1CDCD',
    '#8EE5EE',
    '#8EE5EE',
    '#C1CDCD',
    '#C1CDCD',
    None,
    None,
]


class Status(Enum):
    OK = '#32CD32'
    WARNING = '#FFFF00'
    ERROR = '#FF3030'


class EntryType(Enum):
    RAW = 1
    PHYSICAL = 2
    INVALID = 3


class ValidatingEntry(Entry):
    """
    validating entry widgets

    validate(v: str) -> (raw, status)
    indicate(status, widget) -> None
    """

    def __init__(self, master, validate, indicate, **kwargs):
        """
        Initialisation of entry attributes
        + setting up trace for callback
        """
        super().__init__(master, **kwargs)
        self.indicate = indicate
        self.validate = validate
        self._value = ""
        self._variable = StringVar()
        self._variable.trace('w', self.callback)
        self.config(textvariable=self._variable)
        self.bind('<Return>', self.commit)

    def callback(self, name, mode, index):
        """
        this callback is called whenever the entry field is written.
        the entered value is validated. If validation fails, the background of
        the entry field changes to red, indicating an error to the user.
        """
        raw, status = self.validate(self._variable.get())
        bg_color_indicator(self, status)

    def commit(self, dummy=None):
        val = self._variable.get()
        _, status = self.validate(val)
        if status != Status.ERROR.name:
            self._value = val
        print("Your last Entered Value : {}".format(self._value))

    def get_value(self):
        return self._value

    def set_value(self, value, format):
        # ToDO catch exception if value is not float representation
        if format.startswith('.'):
            self._variable.set("{:{}}".format(float(value), format))
        else:
            self._variable.set("{:{}}".format(int(value), format))



class SignalRow:
    """
    Creates a row to display the attributes of two signals.

    All attributes of a signal will be displayed in individual column based on the user given Row.
    """
    def __init__(self, master, row, signal_details,
                 **kwargs):
        # TODO: signal_details contain FC as well
        self.row = row
        self.gateway = True
        self.signal_active = False
        (self.signal1_details, self.signal2_details) = signal_details

        self._create_entry_measured_value(master, initval_sig1='', initval_sig2='')
        self._create_entry_user_value(master)
        self._create_chkbtn_gateway(master)
        self._create_chkbtn_signal_active(master)
        #self._create_chkbtns_bitfield(master, row, 16, 79)

        self._create_signal_label(master, row=row, column=0,
                                  signame=self.signal1_details.name,
                                  minimum=self.signal1_details.minimum,
                                  maximum=self.signal1_details.maximum,
                                  unit=self.signal1_details.unit,
                                  )
        if self.signal2_details is not None:
            self._create_signal_label(master, row=row, column=3,
                                      signame=self.signal2_details.name,
                                      minimum=self.signal2_details.minimum,
                                      maximum=self.signal2_details.maximum,
                                      unit=self.signal2_details.unit,
                                      )

    def commit(self, dummy=None):
        self.entry_sig1.commit()
        if self.signal2_details is not None:
            self.entry_sig2.commit()

    def _create_signal_label(self, master, row, column, signame, minimum, maximum, unit):
        """
        Creates label for representing the signal 1 & 2 with four main attributes (name, min, max, unit) at the
        user defined row position in the GUI.
        Args:
            master =  Main tkinter frame
            row = Row position given by the user.
            column = Selected column position during the private method call.
            signame = Given names of Signal 1 & 2 during the private method call.
            minimum = Given minimum range of Signal 1 & 2.
            maximum = Given maximum range of Signal 1 & 2.
            unit = Given unit of Signal 1 & 2.
        """
        lbl_name = Label(master, text=signame, bg=COLUMN_COLOR_LIST[column], font=("Helvetica", 12))
        lbl_min = Label(master, text=minimum, bg=COLUMN_COLOR_LIST[column], font=("Helvetica", 9))
        lbl_max = Label(master, text=maximum, bg=COLUMN_COLOR_LIST[column + 1], font=("Helvetica", 9))
        lbl_unit = Label(master, text=unit, bg=COLUMN_COLOR_LIST[column + 2], font=("Helvetica", 9))
        lbl_name.grid(row=row, column=column, columnspan=3, sticky=W+E)
        lbl_min.grid(row=row+1, column=column, sticky=W+E)
        lbl_max.grid(row=row+1, column=column+1, sticky=W+E)
        lbl_unit.grid(row=row+1, column=column+2, sticky=W+E)

    def _create_entry_measured_value(self, master, initval_sig1, initval_sig2):
        """
        Creates Entry for the measured value of the signal 1 & 2. Default is set to empty string.
        Args:
            master =  Main tkinter frame
            initial_value = Initial Value of the measured signal; default = " ".
        """
        self.entry_measured_value_sig1 = StringVar()
        self.entry_measured_value_sig2 = StringVar()
        self.set_measured_value(initval_sig1, initval_sig2)
        entry_sig1 = Entry(master, textvariable=self.entry_measured_value_sig1, width=28)
        entry_sig2 = Entry(master, textvariable=self.entry_measured_value_sig2, width=28)
        entry_sig1.grid(row=self.row, column=6)
        entry_sig2.grid(row=self.row, column=8)
        empty_lbl_1 = Label(master, text="", bg=COLUMN_COLOR_LIST[6], width=24)
        empty_lbl_2 = Label(master, text="", bg=COLUMN_COLOR_LIST[8], width=24)
        empty_lbl_1.grid(row=self.row+1, column=6)
        empty_lbl_2.grid(row=self.row+1, column=8)


    def _create_entry_user_value(self, master):
        """
        Creates Entry for the User given value for the signal 1 & 2. Default is set to empty string.
        Args:
            master =  Main tkinter frame
        """
        self.entry_sig1 = ValidatingEntry(master, validate=self.signal1_details.validate,
                                          indicate=self.signal1_details.indicate, width=28)
        self.entry_sig1.grid(row=self.row,column=7)
        self.entry_sig1.set_value(self.signal1_details.default, self.signal1_details.format)
        if self.signal2_details is not None:
            self.entry_sig2 = ValidatingEntry(master, validate=self.signal2_details.validate,
                                              indicate=self.signal2_details.indicate, width=28)
            self.entry_sig2.grid(row=self.row,column=9)

            self.entry_sig2.set_value(self.signal2_details.default, self.signal2_details.format)
        empty_lbl_1 = Label(master, text="", bg=COLUMN_COLOR_LIST[7], width=24)
        empty_lbl_2 = Label(master, text="", bg=COLUMN_COLOR_LIST[9], width=24)
        empty_lbl_1.grid(row=self.row+1, column=7)
        empty_lbl_2.grid(row=self.row+1, column=9)

    def _create_chkbtn_gateway(self, master):
        """
        Creates CheckButton for selecting the Gateway mode of the signal 1 & signal 2. Default is set to True.
        Args:
            master =  Main tkinter frame
        """
        self.chkbtn_gateway = BooleanVar()
        self.set_gateway(self.gateway)
        chkbtn_gateway = Checkbutton(master, text="Gateway", variable=self.chkbtn_gateway)
        chkbtn_gateway.grid(row=self.row, column=10)

    def _create_chkbtn_signal_active(self, master):
        """
        Creates CheckButton for selecting the Active mode of the signal 1 & signal 2. Default is set to False.
        Args:
            master =  Main tkinter frame
        """
        self.chkbtn_signal_active = BooleanVar()
        self.set_signal_active(self.signal_active)
        chkbtn_sig_act = Checkbutton(master, text="Signal Active", variable=self.signal_active)
        chkbtn_sig_act.grid(row=self.row, column=11)


    def get_user_value(self):
        user_value_sig1 = self.entry_sig1.get_value()
        user_value_sig2 = self.entry_sig2.get_value()

        return user_value_sig1, user_value_sig2

    def set_measured_value(self, value_sig1, value_sig2):
        """
        Set the measured values for 2 signals in the respective Measured value Entry field.
        Args:
            value_sig1 & value_sig2  = To set measured values for 2 signals.
        """
        self.entry_measured_value_sig1.set(value_sig1)
        self.entry_measured_value_sig2.set(value_sig2)

    def get_gateway(self):
        """Get the current status of Gateway CheckButton."""
        return self.gateway

    def set_gateway(self, bool_value):
        """
        Set the status of Gateway CheckButton.
        Args:
           bool_value = True/False or 0/1 which needed to set for changing the Gateway status.
        """
        self.chkbtn_gateway.set(bool_value)

    def get_signal_active(self):
        """Get the current status of Signal Active CheckButton."""
        return self.signal_active

    def set_signal_active(self, bool_value):
        """
        Set the status of Signal Active CheckButton.
        Args:
           bool_value = True/False or 0/1 which needed to set for changing the Signal Active status.
        """
        self.chkbtn_signal_active.set(bool_value)


def bg_color_indicator(widget, status):
    if status == Status.OK.name:
        widget.config(bg=Status.OK.value)
    elif status == Status.WARNING.name:
        widget.config(bg=Status.WARNING.value)
    else:
        widget.config(bg=Status.ERROR.value)


def bitfield_indicator(default_value):
    indicator_list = list(bin(default_value))[2:]
    if '1' in indicator_list:
        return True
    else:
        return False





