object FormMetaspriteExportSettings: TFormMetaspriteExportSettings
  Left = 0
  Top = 0
  BorderStyle = bsToolWindow
  Caption = 'Misc. Metasprite Export Settings'
  ClientHeight = 251
  ClientWidth = 347
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  OnClose = FormClose
  OnDeactivate = FormDeactivate
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object GroupBox1: TGroupBox
    Left = 5
    Top = 0
    Width = 337
    Height = 81
    Caption = 'Add custom offset'
    TabOrder = 0
    object BtnThisSession: TSpeedButton
      Left = 146
      Top = 20
      Width = 110
      Height = 16
      Caption = 'x0 y0'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = BtnThisSessionClick
    end
    object Btn32x30: TSpeedButton
      Left = 146
      Top = 38
      Width = 110
      Height = 16
      Caption = 'x64 y64'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = Btn32x30Click
    end
    object SpeedButton1: TSpeedButton
      Left = 146
      Top = 56
      Width = 110
      Height = 16
      Caption = 'x128 y128'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton1Click
    end
    object BtnIncX: TSpeedButton
      Left = 12
      Top = 20
      Width = 33
      Height = 14
      Caption = 'x +16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object BtnIncY: TSpeedButton
      Left = 74
      Top = 20
      Width = 33
      Height = 14
      Caption = 'y +16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object BtnDecY: TSpeedButton
      Left = 74
      Top = 58
      Width = 33
      Height = 14
      Caption = 'y -16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object BtnDecX: TSpeedButton
      Left = 12
      Top = 58
      Width = 33
      Height = 14
      Caption = 'x -16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object BtnNegateY: TSpeedButton
      Left = 109
      Top = 20
      Width = 22
      Height = 14
      Caption = '+/-'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = BtnNegateYClick
    end
    object BtnNegateX: TSpeedButton
      Left = 47
      Top = 58
      Width = 22
      Height = 14
      Caption = '+/-'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = BtnNegateXClick
    end
    object UpDownOffsetY: TUpDown
      Left = 107
      Top = 35
      Width = 16
      Height = 21
      Associate = EditOffsetY
      Min = -256
      Max = 256
      Position = 128
      TabOrder = 0
      Thousands = False
    end
    object EditOffsetY: TEdit
      Left = 74
      Top = 35
      Width = 33
      Height = 21
      TabOrder = 1
      Text = '128'
      OnClick = EditOffsetXClick
      OnExit = EditOffsetYExit
      OnKeyPress = EditOffsetXKeyPress
    end
    object EditOffsetX: TEdit
      Left = 12
      Top = 35
      Width = 33
      Height = 21
      TabOrder = 2
      Text = '128'
      OnClick = EditOffsetXClick
      OnExit = EditOffsetXExit
      OnKeyPress = EditOffsetXKeyPress
    end
    object UpDownOffsetX: TUpDown
      Left = 45
      Top = 35
      Width = 16
      Height = 21
      Associate = EditOffsetX
      Min = -256
      Max = 256
      Position = 128
      TabOrder = 3
      Thousands = False
    end
    object CheckOffset: TCheckBox
      Left = 266
      Top = 20
      Width = 60
      Height = 17
      Caption = 'Enabled'
      TabOrder = 4
      OnClick = CheckOffsetClick
    end
  end
  object GroupBox2: TGroupBox
    Left = 5
    Top = 82
    Width = 337
    Height = 101
    Caption = 'Stop && Warn if outside custom bounds'
    TabOrder = 1
    object SpeedButton5: TSpeedButton
      Left = 12
      Top = 20
      Width = 33
      Height = 14
      Caption = '+16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object SpeedButton6: TSpeedButton
      Left = 74
      Top = 20
      Width = 33
      Height = 14
      Caption = '+16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object SpeedButton7: TSpeedButton
      Left = 74
      Top = 58
      Width = 33
      Height = 14
      Caption = '-16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object SpeedButton8: TSpeedButton
      Left = 12
      Top = 58
      Width = 33
      Height = 14
      Caption = '-16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object Label1: TLabel
      Left = 56
      Top = 17
      Width = 10
      Height = 13
      Caption = 'x:'
    end
    object SpeedButton2: TSpeedButton
      Left = 147
      Top = 20
      Width = 33
      Height = 14
      Caption = '+16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object Label2: TLabel
      Left = 191
      Top = 17
      Width = 10
      Height = 13
      Caption = 'y:'
    end
    object SpeedButton3: TSpeedButton
      Left = 209
      Top = 20
      Width = 33
      Height = 14
      Caption = '+16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object SpeedButton9: TSpeedButton
      Left = 147
      Top = 58
      Width = 33
      Height = 14
      Caption = '-16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object SpeedButton10: TSpeedButton
      Left = 209
      Top = 58
      Width = 33
      Height = 14
      Caption = '-16'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object SpeedButton19: TSpeedButton
      Left = 12
      Top = 78
      Width = 60
      Height = 14
      Caption = '-64 .. 63'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton19Click
    end
    object SpeedButton20: TSpeedButton
      Left = 76
      Top = 78
      Width = 60
      Height = 14
      Caption = '-127 .. 127'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton20Click
    end
    object SpeedButton21: TSpeedButton
      Left = 140
      Top = 78
      Width = 60
      Height = 14
      Caption = '-128 .. 127'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton21Click
    end
    object SpeedButton22: TSpeedButton
      Left = 204
      Top = 78
      Width = 60
      Height = 14
      Caption = '0 .. 254'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton22Click
    end
    object SpeedButton23: TSpeedButton
      Left = 270
      Top = 78
      Width = 60
      Height = 14
      Caption = '0 .. 255'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton23Click
    end
    object UpDownWarnHiX: TUpDown
      Left = 107
      Top = 35
      Width = 16
      Height = 21
      Associate = EditWarnHiX
      Min = -256
      Max = 256
      Position = 63
      TabOrder = 0
      Thousands = False
    end
    object EditWarnHiX: TEdit
      Left = 74
      Top = 35
      Width = 33
      Height = 21
      TabOrder = 1
      Text = '63'
      OnClick = EditOffsetXClick
      OnExit = EditWarnHiXExit
      OnKeyPress = EditOffsetXKeyPress
    end
    object EditWarnLoX: TEdit
      Left = 12
      Top = 35
      Width = 33
      Height = 21
      TabOrder = 2
      Text = '-64'
      OnClick = EditOffsetXClick
      OnExit = EditWarnLoXExit
      OnKeyPress = EditOffsetXKeyPress
    end
    object UpDownWarnLoX: TUpDown
      Left = 45
      Top = 35
      Width = 16
      Height = 21
      Associate = EditWarnLoX
      Min = -256
      Max = 255
      Position = -64
      TabOrder = 3
      Thousands = False
    end
    object CheckWarn: TCheckBox
      Left = 266
      Top = 20
      Width = 60
      Height = 17
      Caption = 'Enabled'
      TabOrder = 4
      OnClick = CheckOffsetClick
    end
    object EditWarnLoY: TEdit
      Left = 147
      Top = 35
      Width = 33
      Height = 21
      TabOrder = 5
      Text = '-64'
      OnClick = EditOffsetXClick
      OnExit = EditWarnLoYExit
      OnKeyPress = EditOffsetXKeyPress
    end
    object UpDownWarnLoY: TUpDown
      Left = 180
      Top = 35
      Width = 16
      Height = 21
      Associate = EditWarnLoY
      Min = -256
      Max = 256
      Position = -64
      TabOrder = 6
      Thousands = False
    end
    object EditWarnHiY: TEdit
      Left = 209
      Top = 35
      Width = 33
      Height = 21
      TabOrder = 7
      Text = '63'
      OnClick = EditOffsetXClick
      OnExit = EditWarnHiYExit
      OnKeyPress = EditOffsetXKeyPress
    end
    object UpDownWarnHiY: TUpDown
      Left = 242
      Top = 35
      Width = 16
      Height = 21
      Associate = EditWarnHiY
      Min = -256
      Max = 256
      Position = 63
      TabOrder = 8
      Thousands = False
    end
    object CheckJustWarn: TCheckBox
      Left = 266
      Top = 39
      Width = 66
      Height = 17
      Caption = 'Just warn'
      TabOrder = 9
      OnClick = CheckOffsetClick
    end
  end
  object GroupBox3: TGroupBox
    Left = 5
    Top = 184
    Width = 337
    Height = 65
    Caption = 'Custom NES OAM struct order'
    TabOrder = 2
    object btnOAM0: TSpeedButton
      Left = 25
      Top = 20
      Width = 33
      Height = 14
      Caption = 'X'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = btnOAM0Click
    end
    object btnOAM1: TSpeedButton
      Tag = 1
      Left = 79
      Top = 20
      Width = 33
      Height = 14
      Caption = 'Y'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = btnOAM0Click
    end
    object btnOAM2: TSpeedButton
      Tag = 2
      Left = 135
      Top = 20
      Width = 33
      Height = 14
      Caption = 'ID'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = btnOAM0Click
    end
    object btnOAM3: TSpeedButton
      Tag = 3
      Left = 187
      Top = 20
      Width = 33
      Height = 14
      Caption = 'Attr'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = btnOAM0Click
    end
    object SpeedButton12: TSpeedButton
      Left = 12
      Top = 38
      Width = 100
      Height = 16
      Caption = 'NESST (X,Y,ID,Attr)'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton12Click
    end
    object Label3: TLabel
      Left = 12
      Top = 20
      Width = 10
      Height = 13
      Caption = '1:'
    end
    object Label4: TLabel
      Left = 67
      Top = 20
      Width = 10
      Height = 13
      Caption = '2:'
    end
    object Label5: TLabel
      Left = 123
      Top = 20
      Width = 10
      Height = 13
      Caption = '3:'
    end
    object Label6: TLabel
      Left = 175
      Top = 20
      Width = 10
      Height = 13
      Caption = '4:'
    end
    object SpeedButton13: TSpeedButton
      Left = 120
      Top = 38
      Width = 116
      Height = 16
      Caption = 'NES OAM (Y,ID,Attr,X)'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton13Click
    end
    object SpeedButton16: TSpeedButton
      Left = 244
      Top = 38
      Width = 80
      Height = 16
      Caption = 'Y,X,ID,Attr'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton16Click
    end
    object CheckCustomOrder: TCheckBox
      Left = 266
      Top = 20
      Width = 60
      Height = 17
      Caption = 'Enabled'
      TabOrder = 0
      OnClick = CheckOffsetClick
    end
  end
  object PopupMenu1: TPopupMenu
    Left = 160
    Top = 128
    object X1: TMenuItem
      AutoCheck = True
      Caption = 'X'
      Checked = True
      RadioItem = True
      OnClick = X1Click
    end
    object Y1: TMenuItem
      Tag = 1
      AutoCheck = True
      Caption = 'Y'
      RadioItem = True
      OnClick = X1Click
    end
    object ID1: TMenuItem
      Tag = 2
      AutoCheck = True
      Caption = 'tile ID'
      RadioItem = True
      OnClick = X1Click
    end
    object Attributes1: TMenuItem
      Tag = 3
      AutoCheck = True
      Caption = 'Attributes'
      RadioItem = True
      OnClick = X1Click
    end
  end
end
