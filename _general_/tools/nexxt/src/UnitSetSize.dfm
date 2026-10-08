object FormSetSize: TFormSetSize
  Left = 0
  Top = 0
  BorderStyle = bsDialog
  Caption = 'Set canvas size'
  ClientHeight = 148
  ClientWidth = 312
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poMainFormCenter
  Scaled = False
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object GroupBox1: TGroupBox
    Left = 0
    Top = 0
    Width = 312
    Height = 148
    Align = alClient
    TabOrder = 0
    ExplicitWidth = 293
    object BtnWdtInc: TSpeedButton
      Left = 12
      Top = 20
      Width = 33
      Height = 14
      Caption = 'w+32'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = BtnWdtIncClick
    end
    object BtnHgtInc: TSpeedButton
      Left = 74
      Top = 20
      Width = 33
      Height = 14
      Caption = 'h+30'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = BtnHgtIncClick
    end
    object BtnWdtDec: TSpeedButton
      Left = 12
      Top = 58
      Width = 33
      Height = 14
      Caption = 'w -32'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = BtnWdtDecClick
    end
    object BtnHgtDec: TSpeedButton
      Left = 74
      Top = 58
      Width = 33
      Height = 14
      Caption = 'h -30'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = BtnHgtDecClick
    end
    object Btn32x30: TSpeedButton
      Left = 186
      Top = 38
      Width = 119
      Height = 16
      Caption = '1 full NES screen (32x30)'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = Btn32x30Click
    end
    object BtnThisSession: TSpeedButton
      Left = 186
      Top = 20
      Width = 119
      Height = 16
      Caption = 'Reset to current dimensions'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = BtnThisSessionClick
    end
    object SpeedButton1: TSpeedButton
      Left = 186
      Top = 56
      Width = 119
      Height = 16
      Caption = '4 full NES screens (64x60)'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnClick = SpeedButton1Click
    end
    object Label1: TLabel
      Left = 12
      Top = 79
      Width = 12
      Height = 13
      Caption = 'xy'
    end
    object ButtonCancel: TButton
      Left = 150
      Top = 117
      Width = 75
      Height = 25
      Cancel = True
      Caption = 'Cancel'
      TabOrder = 3
      TabStop = False
      OnClick = ButtonCancelClick
    end
    object ButtonOK: TButton
      Left = 230
      Top = 117
      Width = 75
      Height = 25
      Caption = 'OK'
      Default = True
      TabOrder = 0
      TabStop = False
      OnClick = ButtonOKClick
    end
    object EditWidth: TEdit
      Left = 12
      Top = 35
      Width = 33
      Height = 21
      TabOrder = 1
      Text = '32'
      OnClick = EditWidthClick
      OnExit = EditWidthExit
      OnKeyPress = EditWidthKeyPress
    end
    object EditHeight: TEdit
      Left = 74
      Top = 35
      Width = 33
      Height = 21
      TabOrder = 2
      Text = '30'
      OnClick = EditWidthClick
      OnExit = EditHeightExit
      OnKeyPress = EditWidthKeyPress
    end
    object UpDownWidth: TUpDown
      Left = 47
      Top = 35
      Width = 17
      Height = 21
      Associate = EditWidth
      Min = 4
      Max = 4096
      Increment = 4
      Position = 32
      TabOrder = 5
      Thousands = False
      OnClick = UpDownWidthClick
    end
    object UpDownHeight: TUpDown
      Left = 109
      Top = 35
      Width = 17
      Height = 21
      Associate = EditHeight
      Min = 4
      Max = 4096
      Increment = 4
      Position = 30
      TabOrder = 6
      Thousands = False
      OnClick = UpDownHeightClick
    end
    object CheckBoxClear: TCheckBox
      Left = 12
      Top = 117
      Width = 96
      Height = 17
      Caption = 'Clear contents'
      TabOrder = 4
    end
    object Radio1: TRadioButton
      Left = 140
      Top = 78
      Width = 100
      Height = 17
      Caption = 'in screens && tiles'
      TabOrder = 7
      OnClick = Radio1Click
    end
    object Radio2: TRadioButton
      Left = 248
      Top = 78
      Width = 56
      Height = 17
      Caption = 'in pixels'
      Checked = True
      TabOrder = 8
      TabStop = True
      OnClick = Radio2Click
    end
    object GroupBox2: TGroupBox
      Left = 132
      Top = 12
      Width = 51
      Height = 62
      Caption = 'Align'
      TabOrder = 9
      object btnTL: TSpeedButton
        Left = 3
        Top = 14
        Width = 14
        Height = 14
        GroupIndex = 1
        Down = True
      end
      object btnTC: TSpeedButton
        Left = 18
        Top = 14
        Width = 14
        Height = 14
        GroupIndex = 1
      end
      object btnTR: TSpeedButton
        Left = 33
        Top = 14
        Width = 14
        Height = 14
        GroupIndex = 1
      end
      object btnCL: TSpeedButton
        Left = 3
        Top = 29
        Width = 14
        Height = 14
        GroupIndex = 1
      end
      object btnCC: TSpeedButton
        Left = 18
        Top = 29
        Width = 14
        Height = 14
        GroupIndex = 1
      end
      object btnCR: TSpeedButton
        Left = 33
        Top = 29
        Width = 14
        Height = 14
        GroupIndex = 1
      end
      object btnBL: TSpeedButton
        Left = 3
        Top = 44
        Width = 14
        Height = 14
        GroupIndex = 1
      end
      object btnBC: TSpeedButton
        Left = 18
        Top = 44
        Width = 14
        Height = 14
        GroupIndex = 1
      end
      object btnBR: TSpeedButton
        Left = 33
        Top = 44
        Width = 14
        Height = 14
        GroupIndex = 1
      end
    end
  end
  object CheckNullTile: TCheckBox
    Left = 12
    Top = 98
    Width = 236
    Height = 17
    Caption = 'Use null tile for canvas extension or clearing'
    Checked = True
    State = cbChecked
    TabOrder = 1
  end
end
