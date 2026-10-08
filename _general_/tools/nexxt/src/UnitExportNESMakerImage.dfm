object FormExportNESMakerImage: TFormExportNESMakerImage
  Left = 0
  Top = 0
  BorderStyle = bsDialog
  Caption = 'Export tileset as NESmaker Image...'
  ClientHeight = 124
  ClientWidth = 303
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poMainFormCenter
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object GroupBox1: TGroupBox
    Left = 8
    Top = 2
    Width = 290
    Height = 90
    Caption = 'Which portion do you want to export?'
    TabOrder = 0
    object RadioFull: TRadioButton
      Left = 8
      Top = 16
      Width = 128
      Height = 17
      Caption = 'Full tileset (256 tiles)'
      TabOrder = 0
    end
    object RadioUpper: TRadioButton
      Left = 8
      Top = 32
      Width = 128
      Height = 17
      Caption = 'Upper half (128 tiles)'
      Checked = True
      TabOrder = 1
      TabStop = True
    end
    object RadioLower: TRadioButton
      Left = 8
      Top = 48
      Width = 128
      Height = 17
      Caption = 'Lower half (128 tiles)'
      TabOrder = 2
    end
    object RadioSelection: TRadioButton
      Left = 8
      Top = 64
      Width = 128
      Height = 17
      Caption = 'Current box selection'
      TabOrder = 3
    end
    object Radio1st: TRadioButton
      Left = 152
      Top = 16
      Width = 128
      Height = 17
      Caption = '1st quarter (64 tiles)'
      TabOrder = 4
    end
    object Radio2nd: TRadioButton
      Left = 152
      Top = 32
      Width = 128
      Height = 17
      Caption = '2nd quarter (64 tiles)'
      TabOrder = 5
    end
    object Radio3rd: TRadioButton
      Left = 152
      Top = 48
      Width = 128
      Height = 17
      Caption = '3rd quarter (64 tiles)'
      TabOrder = 6
    end
    object Radio4th: TRadioButton
      Left = 152
      Top = 64
      Width = 128
      Height = 17
      Caption = '4th quarter (64 tiles)'
      TabOrder = 7
    end
  end
  object Button1: TButton
    Left = 222
    Top = 96
    Width = 75
    Height = 25
    Caption = 'Export'
    Default = True
    ModalResult = 1
    TabOrder = 1
  end
  object Button2: TButton
    Left = 139
    Top = 96
    Width = 75
    Height = 25
    Cancel = True
    Caption = 'Cancel'
    ModalResult = 2
    TabOrder = 2
  end
end
