inherited FormImportBMP: TFormImportBMP
  Caption = 'Bitmap Import'
  ClientHeight = 281
  ClientWidth = 517
  ExplicitWidth = 523
  ExplicitHeight = 310
  PixelsPerInch = 96
  TextHeight = 16
  inherited GroupBox1: TGroupBox
    Left = 218
    Width = 299
    Height = 281
    Align = alRight
    Caption = 'Pass 2'
    ExplicitLeft = 218
    ExplicitWidth = 299
    ExplicitHeight = 205
    inherited GroupBox4: TGroupBox
      Top = 216
      ExplicitTop = 216
    end
    inherited GroupBox3: TGroupBox
      Top = 15
      Width = 161
      Height = 113
      Caption = 'Colour id order'
      ExplicitTop = 15
      ExplicitWidth = 161
      ExplicitHeight = 113
    end
    inherited GroupBox2: TGroupBox
      Top = 142
      ExplicitTop = 142
    end
    inherited RadioButton4K: TRadioButton
      Top = 160
      ExplicitTop = 160
    end
    inherited RadioButton8K: TRadioButton
      Top = 160
      ExplicitTop = 160
    end
    inherited RadioButtonSelection: TRadioButton
      Top = 180
      ExplicitTop = 180
    end
    inherited ButtonSwap: TButton
      Top = 244
      Height = 32
      ExplicitTop = 244
      ExplicitHeight = 32
    end
    inherited ButtonCancel: TButton
      Top = 210
      ExplicitTop = 210
    end
    inherited Button1: TButton
      Left = 16
      Top = 37
      ExplicitLeft = 16
      ExplicitTop = 37
    end
    inherited Button2: TButton
      Left = 48
      Top = 37
      ExplicitLeft = 48
      ExplicitTop = 37
    end
    inherited Button3: TButton
      Left = 80
      Top = 37
      ExplicitLeft = 80
      ExplicitTop = 37
    end
    inherited Button4: TButton
      Left = 112
      Top = 37
      ExplicitLeft = 112
      ExplicitTop = 37
    end
    inherited ButtonReset: TButton
      Left = 86
      Top = 71
      ExplicitLeft = 86
      ExplicitTop = 71
    end
    inherited ButtonDarker: TButton
      Left = 86
      Top = 94
      ExplicitLeft = 86
      ExplicitTop = 94
    end
    inherited ButtonBrighter: TButton
      Left = 119
      Top = 94
      ExplicitLeft = 119
      ExplicitTop = 94
    end
    inherited RadioPatternNone: TRadioButton
      Top = 180
      ExplicitTop = 180
    end
    inherited Button5: TButton
      Left = 16
      Top = 94
      Width = 38
      ExplicitLeft = 16
      ExplicitTop = 94
      ExplicitWidth = 38
    end
    inherited Button6: TButton
      Left = 56
      Top = 94
      Width = 22
      ExplicitLeft = 56
      ExplicitTop = 94
      ExplicitWidth = 22
    end
    inherited CheckBox1: TCheckBox
      Left = 224
      Top = 180
      Width = 70
      ExplicitLeft = 224
      ExplicitTop = 180
      ExplicitWidth = 70
    end
    inherited GroupBox5: TGroupBox
      Left = 170
      Top = 15
      Width = 82
      Height = 46
      ExplicitLeft = 170
      ExplicitTop = 15
      ExplicitWidth = 82
      ExplicitHeight = 46
      inherited ButtonCol0: TButton
        Left = 8
        ExplicitLeft = 8
      end
    end
    inherited Button7: TButton
      Left = 48
      Top = 71
      Width = 30
      ExplicitLeft = 48
      ExplicitTop = 71
      ExplicitWidth = 30
    end
    inherited Button8: TButton
      Left = 16
      Top = 71
      Width = 30
      ExplicitLeft = 16
      ExplicitTop = 71
      ExplicitWidth = 30
    end
  end
  object GroupBox6: TGroupBox
    Left = 0
    Top = 0
    Width = 220
    Height = 281
    Align = alLeft
    Caption = 'Pass 1'
    TabOrder = 1
    ExplicitHeight = 205
    object GroupBox8: TGroupBox
      Left = 3
      Top = 14
      Width = 212
      Height = 132
      Caption = 'Options'
      TabOrder = 0
      object Label1: TLabel
        Left = 128
        Top = 19
        Width = 37
        Height = 13
        Caption = '# tiles: '
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -11
        Font.Name = 'Tahoma'
        Font.Style = []
        ParentFont = False
      end
      object BtnWdtInc: TSpeedButton
        Left = 119
        Top = 100
        Width = 33
        Height = 14
        Caption = '+16'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -9
        Font.Name = 'Tahoma'
        Font.Style = []
        ParentFont = False
        OnClick = BtnWdtIncClick
      end
      object SpeedButton1: TSpeedButton
        Left = 119
        Top = 115
        Width = 33
        Height = 14
        Caption = '-16'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -9
        Font.Name = 'Tahoma'
        Font.Style = []
        ParentFont = False
        OnClick = SpeedButton1Click
      end
      object CheckBestOffsets: TCheckBox
        Left = 14
        Top = 17
        Width = 97
        Height = 17
        Caption = 'best offsets'
        TabOrder = 0
        OnClick = CheckBestOffsetsClick
      end
      object CheckLossy: TCheckBox
        Left = 14
        Top = 80
        Width = 97
        Height = 17
        Caption = 'lossy (slow!)'
        TabOrder = 1
        OnClick = CheckBestOffsetsClick
      end
      object CheckDensityThres: TCheckBox
        Left = 14
        Top = 59
        Width = 149
        Height = 17
        Caption = 'pixel density threshold'
        TabOrder = 2
        OnClick = CheckBestOffsetsClick
      end
      object CheckNoAttr: TCheckBox
        Left = 14
        Top = 38
        Width = 87
        Height = 17
        Caption = 'skip attr'
        TabOrder = 3
        OnClick = CheckBestOffsetsClick
      end
      object EditPxThres: TEdit
        Left = 162
        Top = 52
        Width = 27
        Height = 24
        TabOrder = 4
        Text = '8'
        OnChange = CheckBestOffsetsClick
      end
      object UpDown1: TUpDown
        Left = 189
        Top = 52
        Width = 15
        Height = 24
        Associate = EditPxThres
        Max = 64
        Position = 8
        TabOrder = 5
      end
      object CheckMaxTiles: TCheckBox
        Left = 14
        Top = 101
        Width = 104
        Height = 17
        Caption = 'maximum tiles'
        TabOrder = 6
        OnClick = CheckBestOffsetsClick
      end
      object EditMaxTiles: TEdit
        Left = 158
        Top = 100
        Width = 31
        Height = 24
        TabOrder = 7
        Text = '64'
        OnExit = CheckBestOffsetsClick
      end
      object UpDown2: TUpDown
        Left = 189
        Top = 100
        Width = 15
        Height = 24
        Associate = EditMaxTiles
        Min = 1
        Max = 512
        Position = 64
        TabOrder = 8
      end
      object CheckNoPal: TCheckBox
        Left = 87
        Top = 38
        Width = 69
        Height = 17
        Caption = 'skip pal'
        TabOrder = 9
        OnClick = CheckBestOffsetsClick
      end
      object Button9: TButton
        Left = 119
        Top = 79
        Width = 33
        Height = 17
        Caption = '...'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -10
        Font.Name = 'Tahoma'
        Font.Style = []
        ParentFont = False
        TabOrder = 10
        Visible = False
        OnClick = Button9Click
      end
    end
    object GroupBox7: TGroupBox
      Left = 3
      Top = 146
      Width = 212
      Height = 52
      Caption = 'Method'
      TabOrder = 1
      object RadioAsMap: TRadioButton
        Left = 11
        Top = 15
        Width = 178
        Height = 17
        Caption = 'normal (import all) '
        Checked = True
        TabOrder = 0
        TabStop = True
        OnClick = CheckBestOffsetsClick
      end
      object RadioMatched: TRadioButton
        Left = 11
        Top = 31
        Width = 178
        Height = 17
        Caption = 'matched to existing tileset'
        TabOrder = 1
        OnClick = CheckBestOffsetsClick
      end
    end
    object GroupBox9: TGroupBox
      Left = 3
      Top = 198
      Width = 212
      Height = 80
      Caption = 'Interpret incoming colour LUT'
      TabOrder = 2
      object Radio16colours: TRadioButton
        Left = 11
        Top = 17
        Width = 178
        Height = 17
        Caption = '16 colours  ( 4 x 4 )'
        Checked = True
        TabOrder = 0
        TabStop = True
        OnClick = CheckBestOffsetsClick
      end
      object Radio13colours: TRadioButton
        Left = 11
        Top = 34
        Width = 194
        Height = 17
        Caption = '13 colours  ( 1 + 3 x 4 )'
        TabOrder = 1
        OnClick = CheckBestOffsetsClick
      end
      object CheckUseLUToffset: TCheckBox
        Left = 11
        Top = 55
        Width = 140
        Height = 17
        Caption = 'begin reading LUT @'
        TabOrder = 2
        OnClick = CheckBestOffsetsClick
      end
      object Edit1: TEdit
        Left = 158
        Top = 51
        Width = 31
        Height = 24
        TabOrder = 3
        Text = '1'
        OnChange = CheckBestOffsetsClick
      end
      object UpDown3: TUpDown
        Left = 189
        Top = 51
        Width = 16
        Height = 24
        Associate = Edit1
        Max = 240
        Position = 1
        TabOrder = 4
      end
    end
  end
end
