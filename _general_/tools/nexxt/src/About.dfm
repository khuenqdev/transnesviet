object AboutBox: TAboutBox
  Left = 200
  Top = 128
  BorderStyle = bsDialog
  Caption = 'About'
  ClientHeight = 271
  ClientWidth = 454
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  OldCreateOrder = True
  Position = poDesigned
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object OKButton: TButton
    Left = 354
    Top = 240
    Width = 96
    Height = 25
    Caption = 'OK'
    Default = True
    ModalResult = 1
    TabOrder = 0
    OnClick = OKButtonClick
  end
  object btnItch: TButton
    Left = 354
    Top = 8
    Width = 96
    Height = 25
    Caption = 'NEXXT@ Itch.io'
    TabOrder = 1
    OnClick = btnItchClick
  end
  object btnCommunity: TButton
    Left = 354
    Top = 36
    Width = 96
    Height = 25
    Caption = 'NEXXT forums'
    TabOrder = 2
    OnClick = btnCommunityClick
  end
  object btnBsky: TButton
    Left = 354
    Top = 112
    Width = 96
    Height = 25
    Caption = 'Bluesky'
    TabOrder = 3
    OnClick = btnBskyClick
  end
  object btnPatreon: TButton
    Left = 354
    Top = 168
    Width = 96
    Height = 25
    Caption = 'Patreon'
    TabOrder = 4
    OnClick = btnPatreonClick
  end
  object btnShiru: TButton
    Left = 354
    Top = 84
    Width = 96
    Height = 25
    Caption = 'Shiru'#39's page'
    TabOrder = 5
    OnClick = btnShiruClick
  end
  object btnMasto: TButton
    Left = 354
    Top = 140
    Width = 60
    Height = 25
    Caption = 'Mastodon'
    TabOrder = 6
    OnClick = btnMastoClick
  end
  object ScrollBox1: TScrollBox
    Left = 8
    Top = 8
    Width = 340
    Height = 256
    HorzScrollBar.Smooth = True
    VertScrollBar.Tracking = True
    TabOrder = 7
    object ProductName: TLabel
      Left = 8
      Top = 4
      Width = 62
      Height = 28
      Caption = 'NEXXT'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -24
      Font.Name = 'Bauhaus 93'
      Font.Style = []
      ParentFont = False
      IsControl = True
    end
    object StaticText1: TStaticText
      Left = 8
      Top = 38
      Width = 58
      Height = 17
      Caption = 'StaticText1'
      TabOrder = 0
    end
  end
  object btnX: TButton
    Left = 416
    Top = 140
    Width = 34
    Height = 25
    Caption = '" X "'
    TabOrder = 8
    OnClick = btnXClick
  end
  object Button1: TButton
    Left = 354
    Top = 198
    Width = 96
    Height = 25
    Caption = 'Ko-Fi'
    TabOrder = 9
    OnClick = Button1Click
  end
end
