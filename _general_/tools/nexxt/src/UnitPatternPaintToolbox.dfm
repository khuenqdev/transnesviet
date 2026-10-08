object FormPatternPaint: TFormPatternPaint
  Left = 0
  Top = 0
  BorderStyle = bsToolWindow
  Caption = 'Pattern paint toolbox'
  ClientHeight = 141
  ClientWidth = 190
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object GroupBox1: TGroupBox
    Left = 3
    Top = 48
    Width = 185
    Height = 44
    Caption = 'Apply to'
    TabOrder = 0
    object btnPen: TSpeedButton
      Left = 4
      Top = 16
      Width = 24
      Height = 22
      AllowAllUp = True
      GroupIndex = 6
      Down = True
      Caption = 'Pen'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btnPenMouseEnter
    end
    object btnBucket: TSpeedButton
      Left = 60
      Top = 16
      Width = 36
      Height = 22
      AllowAllUp = True
      GroupIndex = 8
      Down = True
      Caption = 'Bucket'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btnBucketMouseEnter
    end
    object btnLine: TSpeedButton
      Left = 97
      Top = 16
      Width = 24
      Height = 22
      AllowAllUp = True
      GroupIndex = 9
      Down = True
      Caption = 'Line'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btnLineMouseEnter
    end
    object btnInks: TSpeedButton
      Left = 122
      Top = 16
      Width = 58
      Height = 22
      GroupIndex = 10
      Caption = 'Special inks'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      Visible = False
    end
    object btnBrush: TSpeedButton
      Left = 29
      Top = 16
      Width = 30
      Height = 22
      AllowAllUp = True
      GroupIndex = 7
      Down = True
      Caption = 'Brush'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btnBrushMouseEnter
    end
  end
  object GroupBox2: TGroupBox
    Left = 3
    Top = 5
    Width = 185
    Height = 44
    Caption = 'Apply colours'
    TabOrder = 1
    object btn0: TSpeedButton
      Left = 4
      Top = 16
      Width = 28
      Height = 22
      AllowAllUp = True
      GroupIndex = 1
      Down = True
      Caption = '0'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btn0MouseEnter
    end
    object btn1: TSpeedButton
      Left = 33
      Top = 16
      Width = 28
      Height = 22
      AllowAllUp = True
      GroupIndex = 2
      Down = True
      Caption = '1'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btn1MouseEnter
    end
    object btn2: TSpeedButton
      Left = 62
      Top = 16
      Width = 28
      Height = 22
      AllowAllUp = True
      GroupIndex = 3
      Down = True
      Caption = '2'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btn2MouseEnter
    end
    object btn3: TSpeedButton
      Left = 91
      Top = 16
      Width = 28
      Height = 22
      AllowAllUp = True
      GroupIndex = 4
      Down = True
      Caption = '3'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btn3MouseEnter
    end
    object btnMaskMode: TSpeedButton
      Left = 120
      Top = 16
      Width = 60
      Height = 22
      GroupIndex = 5
      Caption = 'Mask mode'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -10
      Font.Name = 'Tahoma'
      Font.Style = []
      ParentFont = False
      OnMouseEnter = btnMaskModeMouseEnter
    end
  end
  object GroupBox3: TGroupBox
    Left = 3
    Top = 92
    Width = 185
    Height = 44
    Caption = 'Pattern source'
    TabOrder = 2
    object Label1: TLabel
      Left = 36
      Top = 18
      Width = 122
      Height = 13
      Caption = 'Coming in a later version!'
    end
  end
end
