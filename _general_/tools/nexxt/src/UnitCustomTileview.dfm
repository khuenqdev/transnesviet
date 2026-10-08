object FormCustomTileview: TFormCustomTileview
  Tag = 1
  Left = 0
  Top = 0
  BorderStyle = bsToolWindow
  Caption = 'Custom Tileview (using charmap tables)'
  ClientHeight = 332
  ClientWidth = 263
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  OnCreate = FormCreate
  OnMouseLeave = SpeedButton1MouseLeave
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object ImageTileview: TImage
    Left = 4
    Top = 4
    Width = 256
    Height = 256
    OnDragDrop = ImageTileviewDragDrop
    OnDragOver = ImageTileviewDragOver
    OnEndDrag = ImageTileviewEndDrag
    OnMouseDown = ImageTileviewMouseDown
    OnMouseEnter = ImageTileviewMouseEnter
    OnMouseLeave = ImageTileviewMouseLeave
    OnMouseMove = ImageTileviewMouseMove
  end
  object SpeedButton1: TSpeedButton
    Left = 4
    Top = 266
    Width = 84
    Height = 22
    Caption = 'Load .charmap'
    OnClick = SpeedButton1Click
    OnMouseEnter = SpeedButton1MouseEnter
    OnMouseLeave = SpeedButton1MouseLeave
  end
  object SpeedButton2: TSpeedButton
    Left = 90
    Top = 266
    Width = 84
    Height = 22
    Caption = 'Save .charmap'
    OnClick = SpeedButton2Click
    OnMouseEnter = SpeedButton2MouseEnter
    OnMouseLeave = SpeedButton1MouseLeave
  end
  object SpeedButton3: TSpeedButton
    Left = 176
    Top = 266
    Width = 84
    Height = 22
    Caption = 'Reset to ...'
    OnClick = SpeedButton3Click
    OnMouseEnter = SpeedButton3MouseEnter
    OnMouseLeave = SpeedButton1MouseLeave
  end
  object GroupBox1: TGroupBox
    Left = 8
    Top = 290
    Width = 250
    Height = 38
    Caption = 'Show tileset as'
    TabOrder = 0
    object RadioPatterns: TRadioButton
      Left = 8
      Top = 16
      Width = 64
      Height = 17
      Caption = 'patterns'
      Checked = True
      TabOrder = 0
      TabStop = True
      OnClick = RadioPatternsClick
      OnMouseEnter = RadioPatternsMouseEnter
      OnMouseLeave = SpeedButton1MouseLeave
    end
    object RadioIDs: TRadioButton
      Left = 80
      Top = 16
      Width = 65
      Height = 17
      Caption = 'tile ID:s'
      TabOrder = 1
      OnClick = RadioPatternsClick
      OnMouseEnter = RadioIDsMouseEnter
      OnMouseLeave = SpeedButton1MouseLeave
    end
    object CheckBox1: TCheckBox
      Left = 156
      Top = 16
      Width = 80
      Height = 17
      Caption = 'Mouse peek'
      Checked = True
      State = cbChecked
      TabOrder = 2
      OnMouseEnter = CheckBox1MouseEnter
      OnMouseLeave = SpeedButton1MouseLeave
    end
  end
  object OpenDialog1: TOpenDialog
    DefaultExt = 'charmap'
    Filter = 'binary (.charmap)|*.charmap|binary (.bin)|*.bin|any file|*.*'
    Title = 'Open Charmap'
    Left = 160
    Top = 192
  end
  object SaveDialog1: TSaveDialog
    DefaultExt = 'charmap'
    Filter = 'binary (.charmap)|*.charmap|binary (.bin)|*.bin|any file|*.*'
    Title = 'Save charmap'
    Left = 200
    Top = 192
  end
  object PopupMenu1: TPopupMenu
    Left = 200
    Top = 224
    object Normal1: TMenuItem
      Caption = 'Normal'
      OnClick = Normal1Click
    end
    object NES8x16mode1: TMenuItem
      Tag = 1
      Caption = 'NES 8x16 mode'
      OnClick = Normal1Click
    end
    object N1: TMenuItem
      Caption = '-'
    end
    object byfrequency1: TMenuItem
      Tag = 10
      Caption = 'by frequency'
      OnClick = Normal1Click
    end
    object bydensity1: TMenuItem
      Tag = 11
      Caption = 'by density'
      OnClick = Normal1Click
    end
    object bydetail1: TMenuItem
      Tag = 12
      Caption = 'by detail'
      OnClick = Normal1Click
    end
    object byedgecontent1: TMenuItem
      Tag = 13
      Caption = 'by edge content'
      OnClick = Normal1Click
    end
    object byselectedcolour1: TMenuItem
      Tag = 14
      Caption = 'by selected colour'
      OnClick = Normal1Click
    end
    object N2: TMenuItem
      Caption = '-'
    end
    object N4x12x21: TMenuItem
      Tag = 20
      Caption = '4x1 -> 2x2'
      OnClick = Normal1Click
    end
    object N4x12x2topdown1: TMenuItem
      Tag = 21
      Caption = '4x1 -> 2x2 top-down'
      OnClick = Normal1Click
    end
    object N16x14x41: TMenuItem
      Tag = 22
      Caption = '16x1 -> 4x4'
      OnClick = Normal1Click
    end
  end
end
