object FormAccessibility: TFormAccessibility
  Left = 0
  Top = 0
  BorderStyle = bsToolWindow
  Caption = 'Colour perception testing filters'
  ClientHeight = 108
  ClientWidth = 215
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object SpeedButton1: TSpeedButton
    Tag = 2
    Left = 5
    Top = 8
    Width = 100
    Height = 22
    AllowAllUp = True
    GroupIndex = 1
    Caption = 'Protanomaly'
    OnClick = SpeedButton1Click
    OnMouseEnter = SpeedButton1MouseEnter
  end
  object SpeedButton2: TSpeedButton
    Tag = 1
    Left = 110
    Top = 8
    Width = 100
    Height = 22
    AllowAllUp = True
    GroupIndex = 1
    Caption = 'Protanopia'
    OnClick = SpeedButton2Click
    OnMouseEnter = SpeedButton1MouseEnter
  end
  object SpeedButton3: TSpeedButton
    Tag = 4
    Left = 5
    Top = 32
    Width = 100
    Height = 22
    AllowAllUp = True
    GroupIndex = 1
    Caption = 'Deuteranomaly'
    OnClick = SpeedButton3Click
    OnMouseEnter = SpeedButton1MouseEnter
  end
  object SpeedButton4: TSpeedButton
    Tag = 3
    Left = 110
    Top = 32
    Width = 100
    Height = 22
    AllowAllUp = True
    GroupIndex = 1
    Caption = 'Deuteranopia'
    OnClick = SpeedButton4Click
    OnMouseEnter = SpeedButton1MouseEnter
  end
  object SpeedButton5: TSpeedButton
    Tag = 5
    Left = 110
    Top = 56
    Width = 100
    Height = 22
    AllowAllUp = True
    GroupIndex = 1
    Caption = 'Tritanopia'
    OnClick = SpeedButton5Click
    OnMouseEnter = SpeedButton1MouseEnter
  end
  object SpeedButton6: TSpeedButton
    Tag = 6
    Left = 4
    Top = 56
    Width = 100
    Height = 22
    AllowAllUp = True
    GroupIndex = 1
    Caption = ' Tritanomaly'
    OnClick = SpeedButton6Click
    OnMouseEnter = SpeedButton1MouseEnter
  end
  object SpeedButton7: TSpeedButton
    Tag = 7
    Left = 5
    Top = 80
    Width = 205
    Height = 22
    AllowAllUp = True
    GroupIndex = 1
    Caption = 'Monochromacy | Achromatopsia'
    OnClick = SpeedButton7Click
    OnMouseEnter = SpeedButton1MouseEnter
  end
end
