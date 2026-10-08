object FormFader: TFormFader
  Left = 0
  Top = 0
  BorderStyle = bsToolWindow
  Caption = 'Fader | Transition Editor [Secret preview - only partly working]'
  ClientHeight = 228
  ClientWidth = 1028
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  OnCreate = FormCreate
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object PaintBoxFader: TPaintBox
    Left = 2
    Top = 2
    Width = 1024
    Height = 136
    OnPaint = PaintBoxFaderPaint
  end
  object PaintBoxSys: TPaintBox
    Left = 354
    Top = 144
    Width = 392
    Height = 64
    Color = clBtnFace
    ParentColor = False
    OnPaint = PaintBoxSysPaint
  end
  object PaintBoxSubpal: TPaintBox
    Left = 750
    Top = 144
    Width = 180
    Height = 36
    OnPaint = PaintBoxSubpalPaint
  end
  object Label1: TLabel
    Left = 354
    Top = 210
    Width = 97
    Height = 13
    Caption = 'base system palette'
  end
  object Label3: TLabel
    Left = 556
    Top = 210
    Width = 88
    Height = 13
    Caption = 'post-fader palette'
  end
  object GroupBox1: TGroupBox
    Left = 2
    Top = 139
    Width = 136
    Height = 87
    Caption = 'Preview on'
    TabOrder = 0
    object CheckBox1: TCheckBox
      Left = 8
      Top = 13
      Width = 40
      Height = 17
      TabStop = False
      Caption = 'BG'
      TabOrder = 0
      OnClick = CheckBox1Click
    end
    object CheckBox2: TCheckBox
      Left = 8
      Top = 29
      Width = 72
      Height = 17
      TabStop = False
      Caption = 'Palettes'
      TabOrder = 1
      OnClick = CheckBox1Click
    end
    object CheckBox3: TCheckBox
      Left = 48
      Top = 13
      Width = 40
      Height = 17
      TabStop = False
      Caption = 'Spr'
      TabOrder = 2
      OnClick = CheckBox1Click
    end
    object CheckBox4: TCheckBox
      Left = 88
      Top = 13
      Width = 40
      Height = 17
      TabStop = False
      Caption = 'CHR'
      TabOrder = 3
      OnClick = CheckBox1Click
    end
    object CheckBox5: TCheckBox
      Left = 8
      Top = 46
      Width = 124
      Height = 17
      TabStop = False
      Caption = 'Metatiles'
      TabOrder = 4
      OnClick = CheckBox1Click
    end
    object CheckBox9: TCheckBox
      Left = 8
      Top = 63
      Width = 110
      Height = 17
      TabStop = False
      Caption = 'Exported Images'
      TabOrder = 5
      OnClick = CheckBox1Click
    end
  end
  object GroupBox2: TGroupBox
    Left = 139
    Top = 139
    Width = 170
    Height = 52
    Caption = 'Fader '
    TabOrder = 1
    object Label2: TLabel
      Left = 132
      Top = 38
      Width = 21
      Height = 11
      Caption = 'steps'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
    end
    object TrackBarMain: TTrackBar
      Left = 2
      Top = 14
      Width = 128
      Height = 30
      Max = 5
      TabOrder = 0
      TabStop = False
      OnChange = TrackBarMainChange
    end
    object Edit1: TEdit
      Left = 128
      Top = 17
      Width = 20
      Height = 19
      TabStop = False
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -9
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      TabOrder = 1
      Text = '6'
    end
    object UpDown1: TUpDown
      Left = 148
      Top = 17
      Width = 14
      Height = 19
      Associate = Edit1
      Min = 2
      Max = 24
      Position = 6
      TabOrder = 2
      OnClick = UpDown1Click
    end
  end
  object GroupBox3: TGroupBox
    Left = 750
    Top = 184
    Width = 180
    Height = 42
    Caption = 'Subpal channels | fader sets'
    TabOrder = 2
    object SpeedButton1: TSpeedButton
      Left = 8
      Top = 16
      Width = 22
      Height = 20
      GroupIndex = 1
      Down = True
      Caption = 'All'
      OnMouseDown = SpeedButton1MouseDown
    end
    object SpeedButton2: TSpeedButton
      Left = 32
      Top = 16
      Width = 24
      Height = 20
      GroupIndex = 1
      Caption = '1'
    end
    object SpeedButton3: TSpeedButton
      Left = 57
      Top = 16
      Width = 24
      Height = 20
      GroupIndex = 1
      Caption = '2'
    end
    object SpeedButton4: TSpeedButton
      Left = 82
      Top = 16
      Width = 24
      Height = 20
      GroupIndex = 1
      Caption = '3'
    end
    object SpeedButton5: TSpeedButton
      Left = 107
      Top = 16
      Width = 24
      Height = 20
      GroupIndex = 1
      Caption = '4'
    end
    object SpeedButton6: TSpeedButton
      Left = 134
      Top = 16
      Width = 20
      Height = 20
      GroupIndex = 2
      Caption = 'A'
      OnMouseDown = SpeedButton6MouseDown
    end
    object SpeedButton7: TSpeedButton
      Left = 155
      Top = 16
      Width = 20
      Height = 20
      GroupIndex = 2
      Caption = 'B'
      OnMouseDown = SpeedButton6MouseDown
    end
  end
  object GroupBox4: TGroupBox
    Left = 310
    Top = 139
    Width = 40
    Height = 87
    Caption = 'PPUM'
    TabOrder = 3
    object ChkG: TCheckBox
      Left = 8
      Top = 29
      Width = 28
      Height = 17
      Caption = 'G'
      TabOrder = 0
      OnClick = ChkGClick
    end
    object ChkR: TCheckBox
      Left = 8
      Top = 13
      Width = 28
      Height = 17
      TabStop = False
      Caption = 'R'
      TabOrder = 1
      OnClick = ChkRClick
    end
    object ChkB: TCheckBox
      Left = 8
      Top = 46
      Width = 28
      Height = 17
      Caption = 'B'
      TabOrder = 2
      OnClick = ChkBClick
    end
    object ChkM: TCheckBox
      Left = 8
      Top = 63
      Width = 28
      Height = 17
      TabStop = False
      Caption = 'M'
      TabOrder = 3
      OnClick = ChkMClick
    end
  end
  object GroupBox5: TGroupBox
    Left = 932
    Top = 139
    Width = 94
    Height = 87
    Caption = 'Colour ID page'
    TabOrder = 4
    object Radio00: TRadioButton
      Left = 8
      Top = 13
      Width = 78
      Height = 17
      Caption = '00-3F (NES)'
      TabOrder = 0
      OnClick = Radio00Click
    end
    object Radio40: TRadioButton
      Left = 8
      Top = 29
      Width = 50
      Height = 17
      Caption = '40-7F'
      TabOrder = 1
      OnClick = Radio00Click
    end
    object Radio80: TRadioButton
      Left = 8
      Top = 46
      Width = 50
      Height = 17
      Caption = '80-BF'
      TabOrder = 2
      OnClick = Radio00Click
    end
    object RadioC0: TRadioButton
      Left = 8
      Top = 63
      Width = 50
      Height = 17
      Caption = 'C0-FF'
      TabOrder = 3
      OnClick = Radio00Click
    end
  end
  object GroupBox6: TGroupBox
    Left = 139
    Top = 190
    Width = 170
    Height = 36
    Caption = 'Metapalette table'
    TabOrder = 5
    object SpeedButton8: TSpeedButton
      Left = 8
      Top = 14
      Width = 48
      Height = 18
      Caption = 'Presets'
      OnClick = SpeedButton8Click
    end
    object SpeedButton9: TSpeedButton
      Left = 60
      Top = 14
      Width = 48
      Height = 18
      Caption = 'Load'
    end
    object SpeedButton10: TSpeedButton
      Left = 112
      Top = 14
      Width = 48
      Height = 18
      Caption = 'Save'
      OnClick = SpeedButton10Click
    end
  end
  object PopupMenuPresets: TPopupMenu
    Left = 504
    Top = 112
    object Subtlefadetoblacks1: TMenuItem
      Caption = 'Subtle fade to blacks'
      object Narrowdown1: TMenuItem
        Caption = 'Narrow down | 6'
      end
      object Narrowtocold1: TMenuItem
        Caption = ' Narrow to cold | 6'
      end
      object Narrowtohot1: TMenuItem
        Caption = ' Narrow to hot | 6'
      end
      object Narrowtomossy1: TMenuItem
        Caption = 'Narrow to mossy | 6'
      end
    end
    object Pronouncedfadetoblacks1: TMenuItem
      Caption = 'Pronounced fade to blacks'
      object Sunburn61: TMenuItem
        Caption = 'Sunburn | 6'
      end
      object urnoffthelights1: TMenuItem
        Caption = 'Turn off the lights'
      end
    end
  end
  object PopupMenuSave: TPopupMenu
    Left = 512
    Top = 120
    object binary1: TMenuItem
      Caption = 'as binary...'
    end
  end
  object PopupMenuAB: TPopupMenu
    Left = 520
    Top = 128
    object alllchannels1: TMenuItem
      Caption = 'all channels'
      object copyAtoB1: TMenuItem
        Caption = 'clone A to B'
      end
      object copyBtoA1: TMenuItem
        Caption = 'clone B to A'
      end
      object swapAB1: TMenuItem
        Caption = 'swap A && B'
      end
    end
    object currentchannelonly1: TMenuItem
      Caption = 'current channel only'
      object copyAtoB2: TMenuItem
        Caption = 'clone A to B'
      end
      object copyBtoA2: TMenuItem
        Caption = 'clone B to A'
      end
      object swapAB2: TMenuItem
        Caption = 'swap A && B'
      end
    end
  end
  object PopupMenuChannel: TPopupMenu
    Left = 528
    Top = 136
    object copythischannel1: TMenuItem
      Caption = 'copy this channel'
    end
    object pastetothischannel1: TMenuItem
      Caption = 'paste to this channel'
    end
    object clonethischanneltoallsubpalchannels1: TMenuItem
      Caption = 'clone this channel to all subpal channels'
    end
  end
end
