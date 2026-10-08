object FormPreferences: TFormPreferences
  Left = 195
  Top = 108
  BorderStyle = bsDialog
  Caption = 'Preferences'
  ClientHeight = 314
  ClientWidth = 563
  Color = clBtnFace
  ParentFont = True
  OldCreateOrder = True
  PopupMode = pmAuto
  Position = poScreenCenter
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 563
    Height = 280
    Align = alClient
    BevelOuter = bvNone
    BorderWidth = 5
    ParentColor = True
    TabOrder = 1
    object PageControl1: TPageControl
      Left = 5
      Top = 5
      Width = 553
      Height = 270
      ActivePage = TabSheet1
      Align = alClient
      TabOrder = 0
      object TabSheet1: TTabSheet
        Caption = 'Startup'
        object RGroupScale: TGroupBox
          Left = 3
          Top = 0
          Width = 131
          Height = 41
          Caption = 'GUI Scale'
          TabOrder = 0
          object RadioScale2x: TRadioButton
            Left = 5
            Top = 16
            Width = 33
            Height = 17
            Caption = '2x'
            TabOrder = 0
          end
          object RadioScale3x: TRadioButton
            Left = 44
            Top = 16
            Width = 33
            Height = 17
            Caption = '3x'
            TabOrder = 1
          end
          object RadioScale4x: TRadioButton
            Left = 77
            Top = 16
            Width = 33
            Height = 17
            Caption = '4x'
            TabOrder = 2
          end
        end
        object RGroupColour: TGroupBox
          Left = 140
          Top = 0
          Width = 130
          Height = 41
          Caption = 'Preselected colour'
          TabOrder = 1
          object RadioCol0: TRadioButton
            Left = 9
            Top = 16
            Width = 25
            Height = 17
            Caption = '0'
            TabOrder = 0
          end
          object RadioCol1: TRadioButton
            Left = 39
            Top = 16
            Width = 25
            Height = 17
            Caption = '1'
            TabOrder = 1
          end
          object RadioCol2: TRadioButton
            Left = 70
            Top = 16
            Width = 29
            Height = 17
            Caption = '2'
            TabOrder = 2
          end
          object RadioCol3: TRadioButton
            Left = 99
            Top = 16
            Width = 25
            Height = 17
            Caption = '3'
            TabOrder = 3
          end
        end
        object RGroupSubpal: TGroupBox
          Left = 276
          Top = 0
          Width = 130
          Height = 41
          Caption = 'Preselected subpalette'
          TabOrder = 2
          object RadioSubpal0: TRadioButton
            Left = 9
            Top = 16
            Width = 28
            Height = 17
            Caption = '0'
            TabOrder = 0
          end
          object RadioSubpal1: TRadioButton
            Left = 38
            Top = 16
            Width = 26
            Height = 17
            Caption = '1'
            TabOrder = 1
          end
          object RadioSubpal2: TRadioButton
            Left = 65
            Top = 16
            Width = 29
            Height = 17
            Caption = '2'
            TabOrder = 2
          end
          object RadioSubpal3: TRadioButton
            Left = 92
            Top = 16
            Width = 25
            Height = 17
            Caption = '3'
            TabOrder = 3
          end
        end
        object RGroupGrid: TGroupBox
          Left = 3
          Top = 42
          Width = 131
          Height = 196
          Caption = 'Grid'
          TabOrder = 3
          object RadioGridHide: TRadioButton
            Left = 5
            Top = 16
            Width = 41
            Height = 17
            Caption = 'Off'
            TabOrder = 0
          end
          object RadioGridShow: TRadioButton
            Left = 55
            Top = 16
            Width = 48
            Height = 17
            Caption = 'On'
            TabOrder = 1
          end
          object CheckGrid1: TCheckBox
            Left = 5
            Top = 32
            Width = 81
            Height = 17
            Caption = 'x1 (tile grid)'
            TabOrder = 2
          end
          object CheckGrid2: TCheckBox
            Left = 5
            Top = 48
            Width = 105
            Height = 17
            Caption = 'x2 (attribute grid)'
            TabOrder = 3
          end
          object CheckGrid4: TCheckBox
            Left = 5
            Top = 64
            Width = 97
            Height = 17
            Caption = 'x4 (block grid)'
            TabOrder = 4
          end
          object CheckGridPixelCHR: TCheckBox
            Left = 5
            Top = 144
            Width = 115
            Height = 17
            Caption = 'Tile Editor: pixels'
            TabOrder = 5
          end
          object CheckGrid32x30: TCheckBox
            Left = 5
            Top = 96
            Width = 97
            Height = 17
            Caption = '32x30 (screen)'
            TabOrder = 6
          end
          object CheckGridTilesCHR: TCheckBox
            Left = 5
            Top = 160
            Width = 115
            Height = 17
            Caption = 'Tile Editor: tiles'
            TabOrder = 7
          end
          object CheckGridMidpointsCHR: TCheckBox
            Left = 5
            Top = 176
            Width = 124
            Height = 17
            Caption = 'Tile Editor: midpoints'
            TabOrder = 8
          end
          object CheckGrid8: TCheckBox
            Left = 5
            Top = 80
            Width = 122
            Height = 17
            Caption = 'x8 (double block grid)'
            TabOrder = 9
          end
        end
        object GroupShowWindow: TGroupBox
          Left = 276
          Top = 42
          Width = 130
          Height = 196
          Caption = 'Show window'
          TabOrder = 4
          object CheckShowCHREditor: TCheckBox
            Left = 5
            Top = 16
            Width = 97
            Height = 17
            Caption = 'Tile editor'
            TabOrder = 0
          end
          object CheckShowMetaspriteManager: TCheckBox
            Left = 5
            Top = 32
            Width = 116
            Height = 17
            Caption = 'Metasprite manager'
            TabOrder = 1
          end
          object CheckShowBrushes: TCheckBox
            Left = 5
            Top = 48
            Width = 116
            Height = 17
            Caption = 'Toolbox: Brushes'
            TabOrder = 2
          end
          object CheckShowBucket: TCheckBox
            Left = 5
            Top = 64
            Width = 116
            Height = 17
            Caption = 'Toolbox: Bucket'
            TabOrder = 3
          end
          object CheckShowLines: TCheckBox
            Left = 5
            Top = 80
            Width = 116
            Height = 17
            Caption = 'Toolbox: Lines'
            TabOrder = 4
          end
          object CheckShowPaste: TCheckBox
            Left = 5
            Top = 96
            Width = 122
            Height = 17
            Caption = 'Toolbox: Spec. paste'
            TabOrder = 5
          end
          object CheckShowBankSelector: TCheckBox
            Left = 5
            Top = 128
            Width = 122
            Height = 17
            Caption = 'Tile bank selector'
            TabOrder = 6
          end
          object CheckShowNavigator: TCheckBox
            Left = 5
            Top = 112
            Width = 122
            Height = 17
            Caption = 'Navigator'
            TabOrder = 7
          end
          object CheckShowMetatileEditor: TCheckBox
            Left = 5
            Top = 160
            Width = 122
            Height = 17
            Caption = 'Metatile editor'
            TabOrder = 8
          end
          object CheckShowColourRose: TCheckBox
            Left = 5
            Top = 176
            Width = 122
            Height = 17
            Caption = 'Colour rose'
            TabOrder = 9
          end
          object CheckShowBankSwapper: TCheckBox
            Left = 5
            Top = 144
            Width = 122
            Height = 17
            Caption = 'Tile bank swapper'
            TabOrder = 10
          end
        end
        object GroupBox15: TGroupBox
          Left = 140
          Top = 42
          Width = 131
          Height = 100
          Caption = 'Metasprite list - show...'
          TabOrder = 5
          object CheckShowMsprListID: TCheckBox
            Left = 5
            Top = 16
            Width = 40
            Height = 17
            Caption = '#'
            TabOrder = 0
          end
          object CheckShowMsprListLabel: TCheckBox
            Left = 50
            Top = 16
            Width = 60
            Height = 17
            Caption = 'Label'
            TabOrder = 1
          end
          object CheckShowMsprListNTSC: TCheckBox
            Left = 5
            Top = 32
            Width = 116
            Height = 17
            Caption = 'NTSC duration'
            TabOrder = 2
          end
          object CheckShowMsprListPAL: TCheckBox
            Left = 5
            Top = 48
            Width = 116
            Height = 17
            Caption = 'PAL duration'
            TabOrder = 3
          end
          object CheckShowMsprListCount: TCheckBox
            Left = 5
            Top = 64
            Width = 116
            Height = 17
            Caption = 'Sprite count'
            TabOrder = 4
          end
          object CheckShowMsprListTag: TCheckBox
            Left = 5
            Top = 80
            Width = 116
            Height = 17
            Caption = 'Playback tags'
            TabOrder = 5
          end
        end
        object GroupBox22: TGroupBox
          Left = 412
          Top = 42
          Width = 130
          Height = 196
          Caption = 'Pin on top behaviour'
          TabOrder = 6
          object CheckPinCHREditor: TCheckBox
            Left = 5
            Top = 16
            Width = 97
            Height = 17
            Caption = 'Tile editor'
            TabOrder = 0
          end
          object CheckPinMetaspriteManager: TCheckBox
            Left = 5
            Top = 32
            Width = 116
            Height = 17
            Caption = 'Metasprite manager'
            TabOrder = 1
          end
          object CheckPinBrushes: TCheckBox
            Left = 5
            Top = 48
            Width = 116
            Height = 17
            Caption = 'Toolbox: Brushes'
            TabOrder = 2
          end
          object CheckPinBucket: TCheckBox
            Left = 5
            Top = 64
            Width = 116
            Height = 17
            Caption = 'Toolbox: Bucket'
            TabOrder = 3
          end
          object CheckPinLines: TCheckBox
            Left = 5
            Top = 80
            Width = 116
            Height = 17
            Caption = 'Toolbox: Lines'
            TabOrder = 4
          end
          object CheckPinPaste: TCheckBox
            Left = 5
            Top = 96
            Width = 122
            Height = 17
            Caption = 'Toolbox: Spec. paste'
            TabOrder = 5
          end
          object CheckPinNavigator: TCheckBox
            Left = 5
            Top = 112
            Width = 122
            Height = 17
            Caption = 'Navigator'
            TabOrder = 6
          end
          object CheckPinBankSelector: TCheckBox
            Left = 5
            Top = 128
            Width = 122
            Height = 17
            Caption = 'Tile bank selector'
            TabOrder = 7
          end
          object CheckPinBankSwapper: TCheckBox
            Left = 5
            Top = 144
            Width = 122
            Height = 17
            Caption = 'Tile bank swapper'
            TabOrder = 8
          end
          object CheckPinMetatileEditor: TCheckBox
            Left = 5
            Top = 160
            Width = 122
            Height = 17
            Caption = 'Metatile editor'
            TabOrder = 9
          end
          object CheckPinColourRose: TCheckBox
            Left = 5
            Top = 176
            Width = 122
            Height = 17
            Caption = 'Colour rose'
            TabOrder = 10
          end
        end
      end
      object TabSheet2: TTabSheet
        Caption = 'Editor'
        object GroupBox3: TGroupBox
          Left = 3
          Top = 3
          Width = 130
          Height = 40
          Caption = 'Recall colour [Z]'
          TabOrder = 8
          object CheckAutostoreLastUsed: TCheckBox
            Left = 9
            Top = 16
            Width = 118
            Height = 17
            Caption = 'autostore last used'
            TabOrder = 0
          end
        end
        object GroupBitmask: TGroupBox
          Left = 137
          Top = 3
          Width = 99
          Height = 111
          Caption = 'Apply bitmask to'
          TabOrder = 2
          object CheckBitmaskPen: TCheckBox
            Left = 11
            Top = 16
            Width = 38
            Height = 17
            Caption = 'Pen'
            TabOrder = 4
          end
          object CheckBitmaskMirror: TCheckBox
            Left = 11
            Top = 32
            Width = 49
            Height = 17
            Caption = 'Mirror'
            TabOrder = 0
          end
          object CheckBitmaskRotate: TCheckBox
            Left = 11
            Top = 48
            Width = 57
            Height = 17
            Caption = 'Rotate'
            TabOrder = 1
          end
          object CheckBitmaskNudge: TCheckBox
            Left = 11
            Top = 64
            Width = 49
            Height = 17
            Caption = 'Nudge'
            TabOrder = 2
          end
          object CheckBitmaskPaste: TCheckBox
            Left = 11
            Top = 80
            Width = 49
            Height = 17
            Caption = 'Paste'
            TabOrder = 3
          end
        end
        object GroupRules: TGroupBox
          Left = 242
          Top = 3
          Width = 164
          Height = 52
          Caption = 'Rules'
          TabOrder = 1
          object CheckRules0F: TCheckBox
            Left = 11
            Top = 16
            Width = 102
            Height = 17
            Caption = 'Use $0F as black'
            TabOrder = 0
          end
          object CheckRulesSharedBG: TCheckBox
            Left = 11
            Top = 32
            Width = 145
            Height = 17
            Caption = 'Shared background colour'
            TabOrder = 1
          end
        end
        object RGroupASCIIBase: TGroupBox
          Left = 242
          Top = 56
          Width = 164
          Height = 40
          Caption = 'Type In ASCII Base Offset'
          TabOrder = 3
          object RadioASCIIneg20: TRadioButton
            Left = 11
            Top = 16
            Width = 45
            Height = 17
            Caption = '-$20'
            TabOrder = 0
          end
          object RadioASCIIneg30: TRadioButton
            Left = 61
            Top = 16
            Width = 45
            Height = 17
            Caption = '-$30'
            TabOrder = 1
          end
          object RadioASCIIneg40: TRadioButton
            Left = 112
            Top = 16
            Width = 45
            Height = 17
            Caption = '-$40'
            TabOrder = 2
          end
        end
        object GroupFindUnused: TGroupBox
          Left = 242
          Top = 98
          Width = 164
          Height = 71
          Caption = 'Find unused'
          TabOrder = 4
          object CheckFindUnusedForce: TCheckBox
            Left = 11
            Top = 16
            Width = 137
            Height = 17
            Caption = 'force: only on active tab'
            TabOrder = 0
          end
          object CheckFindUnusedName: TCheckBox
            Left = 11
            Top = 31
            Width = 142
            Height = 18
            Caption = 'include nametable/map'
            TabOrder = 1
          end
          object CheckFindUnusedMeta: TCheckBox
            Left = 11
            Top = 46
            Width = 113
            Height = 19
            Caption = 'include metasprites'
            TabOrder = 2
          end
        end
        object GroupRemoveFound: TGroupBox
          Left = 242
          Top = 171
          Width = 164
          Height = 54
          Caption = 'Remove found'
          TabOrder = 5
          object CheckRemoveFoundSort: TCheckBox
            Left = 11
            Top = 16
            Width = 129
            Height = 17
            Caption = '+ sort tiles afterwards'
            TabOrder = 0
          end
        end
        object RGroupInkLimit: TGroupBox
          Left = 3
          Top = 120
          Width = 128
          Height = 52
          Caption = 'Inc/dec ink limit'
          TabOrder = 6
          object RadioInkLimitCap: TRadioButton
            Left = 11
            Top = 16
            Width = 41
            Height = 17
            Caption = 'Cap'
            TabOrder = 0
          end
          object RadioInkLimitWrap: TRadioButton
            Left = 11
            Top = 32
            Width = 45
            Height = 17
            Caption = 'Wrap'
            TabOrder = 1
          end
        end
        object RGroupInkBehaviour: TGroupBox
          Left = 3
          Top = 173
          Width = 128
          Height = 52
          Caption = 'Inc/dec ink behaviour'
          TabOrder = 0
          object RadioInkBehaviourClick: TRadioButton
            Left = 11
            Top = 16
            Width = 63
            Height = 17
            Caption = 'Per click'
            TabOrder = 0
          end
          object RadioInkBehaviourDistance: TRadioButton
            Left = 11
            Top = 32
            Width = 97
            Height = 17
            Caption = 'Over distance'
            TabOrder = 1
          end
        end
        object RGroupInkFlow: TGroupBox
          Left = 137
          Top = 120
          Width = 99
          Height = 105
          Caption = 'Inc/dec ink flow'
          TabOrder = 7
          object RadioInkFlowQuickest: TRadioButton
            Left = 11
            Top = 16
            Width = 65
            Height = 17
            Caption = 'Quickest'
            TabOrder = 0
          end
          object RadioInkFlowQuick: TRadioButton
            Left = 11
            Top = 32
            Width = 49
            Height = 17
            Caption = 'Quick'
            TabOrder = 1
          end
          object RadioInkFlowMedium: TRadioButton
            Left = 11
            Top = 48
            Width = 57
            Height = 17
            Caption = 'Medium'
            TabOrder = 2
          end
          object RadioInkFlowSlow: TRadioButton
            Left = 11
            Top = 64
            Width = 49
            Height = 17
            Caption = 'Slow'
            TabOrder = 3
          end
          object RadioInkFlowSlowest: TRadioButton
            Left = 11
            Top = 80
            Width = 62
            Height = 17
            Caption = 'Slowest'
            TabOrder = 4
          end
        end
        object GroupBox18: TGroupBox
          Left = 3
          Top = 42
          Width = 130
          Height = 40
          Caption = 'Anti-Jag [Shift+J]'
          TabOrder = 9
          object CheckAntiJagEnabled: TCheckBox
            Left = 9
            Top = 16
            Width = 118
            Height = 17
            Caption = 'enabled by default'
            TabOrder = 0
          end
        end
      end
      object TabSheet3: TTabSheet
        Caption = 'Import'
        ExplicitLeft = 0
        ExplicitTop = 0
        ExplicitWidth = 0
        ExplicitHeight = 0
        object GroupBMPAsName: TGroupBox
          Left = 3
          Top = 3
          Width = 164
          Height = 139
          Caption = 'PNG / BMP as map'
          TabOrder = 0
          object CheckBMPBestOffsets: TCheckBox
            Left = 11
            Top = 16
            Width = 97
            Height = 17
            Caption = 'Best offsets'
            TabOrder = 0
          end
          object CheckBMPLossy: TCheckBox
            Left = 11
            Top = 32
            Width = 112
            Height = 17
            Caption = 'Lossy import (slow)'
            TabOrder = 1
          end
          object CheckBMPThres: TCheckBox
            Left = 11
            Top = 48
            Width = 97
            Height = 17
            Caption = 'Threshold'
            TabOrder = 3
          end
          object CheckBMPNoColour: TCheckBox
            Left = 11
            Top = 64
            Width = 117
            Height = 17
            Caption = 'Without colour data'
            TabOrder = 2
          end
          object CheckBMPExpect13: TCheckBox
            Left = 11
            Top = 80
            Width = 124
            Height = 17
            Caption = 'Expect 13 colour LUT'
            TabOrder = 4
          end
          object CheckBMPLUToffset: TCheckBox
            Left = 11
            Top = 96
            Width = 96
            Height = 17
            Caption = 'begin LUT at #'
            TabOrder = 5
          end
          object Edit1: TEdit
            Left = 109
            Top = 96
            Width = 31
            Height = 24
            TabOrder = 6
            Text = '1'
          end
          object UpDownLUToff: TUpDown
            Left = 140
            Top = 96
            Width = 16
            Height = 24
            Associate = Edit1
            Max = 240
            Position = 1
            TabOrder = 7
          end
        end
        object GroupBox13: TGroupBox
          Left = 170
          Top = 3
          Width = 212
          Height = 72
          Caption = 'CHR; custom filesizes'
          TabOrder = 1
          object RadioImportCHRWrap: TRadioButton
            Left = 3
            Top = 16
            Width = 204
            Height = 17
            Caption = 'Overflowing data wraps on active set'
            TabOrder = 0
          end
          object RadioImportCHRCarry: TRadioButton
            Left = 3
            Top = 32
            Width = 202
            Height = 17
            Caption = 'Overflowing data carries to other set'
            TabOrder = 1
          end
          object RadioImportCHRSkip: TRadioButton
            Left = 3
            Top = 50
            Width = 180
            Height = 17
            Caption = 'Overflowing data gets ignored'
            TabOrder = 2
          end
        end
      end
      object TabSheet4: TTabSheet
        Caption = 'Export Text'
        object RGroupSpriteMetadata: TGroupBox
          Left = 251
          Top = 3
          Width = 153
          Height = 121
          Caption = 'Sprite export metadata'
          TabOrder = 0
          object RadioNoHeader: TRadioButton
            Left = 11
            Top = 17
            Width = 136
            Height = 16
            Caption = 'No header or terminator'
            TabOrder = 0
          end
          object RadioSpriteCount: TRadioButton
            Left = 11
            Top = 32
            Width = 121
            Height = 17
            Caption = 'Sprite count header'
            TabOrder = 1
          end
          object RadioNflag: TRadioButton
            Left = 11
            Top = 48
            Width = 129
            Height = 17
            Caption = '$80 (N flag) terminator'
            TabOrder = 2
          end
          object RadioFFTerminator: TRadioButton
            Left = 11
            Top = 64
            Width = 113
            Height = 17
            Caption = '$FF terminator'
            TabOrder = 3
          end
          object RadioSingle00: TRadioButton
            Left = 11
            Top = 80
            Width = 113
            Height = 17
            Caption = '$00 terminator'
            TabOrder = 5
          end
          object RadioDouble00: TRadioButton
            Left = 11
            Top = 96
            Width = 129
            Height = 17
            Caption = 'Double $00 terminator'
            TabOrder = 4
          end
        end
        object GroupAskName: TGroupBox
          Left = 251
          Top = 124
          Width = 153
          Height = 115
          Caption = 'Metasprite/bank to clipboard'
          TabOrder = 1
          object CheckAskSprName: TCheckBox
            Left = 11
            Top = 16
            Width = 121
            Height = 17
            Caption = 'Ask metasprite name'
            TabOrder = 0
          end
          object CheckAskBankName: TCheckBox
            Left = 11
            Top = 32
            Width = 97
            Height = 17
            Caption = 'Ask bank name'
            TabOrder = 1
          end
          object CheckIncludeNTSC: TCheckBox
            Left = 11
            Top = 48
            Width = 136
            Height = 17
            Caption = 'Include NTSC animation'
            TabOrder = 2
          end
          object CheckIncludePAL: TCheckBox
            Left = 11
            Top = 64
            Width = 136
            Height = 17
            Caption = 'Include PAL animation'
            TabOrder = 3
          end
          object CheckForMsprBanks: TCheckBox
            Left = 30
            Top = 80
            Width = 83
            Height = 17
            Caption = '...for banks'
            TabOrder = 4
          end
          object CheckForMsprSingles: TCheckBox
            Left = 30
            Top = 95
            Width = 91
            Height = 17
            Caption = '...for singles'
            TabOrder = 5
          end
        end
        object GroupAsmSyntax: TGroupBox
          Left = 3
          Top = 124
          Width = 102
          Height = 42
          Caption = 'Asm directive:'
          TabOrder = 2
          object RadioAsmByte: TRadioButton
            Left = 11
            Top = 16
            Width = 48
            Height = 17
            Caption = '.byte'
            TabOrder = 0
          end
          object RadioAsmDb: TRadioButton
            Left = 62
            Top = 16
            Width = 34
            Height = 17
            Caption = '.db'
            TabOrder = 1
          end
        end
        object GroupBox1: TGroupBox
          Left = 3
          Top = 3
          Width = 129
          Height = 80
          Caption = 'Save map/screen'
          TabOrder = 3
          object CheckIncludeNames: TCheckBox
            Left = 11
            Top = 16
            Width = 105
            Height = 17
            Caption = 'Include names'
            TabOrder = 0
          end
          object CheckIncludeAttributes: TCheckBox
            Left = 11
            Top = 32
            Width = 105
            Height = 17
            Caption = 'Include attributes'
            TabOrder = 1
          end
          object CheckRLECompress: TCheckBox
            Left = 11
            Top = 48
            Width = 105
            Height = 17
            Caption = 'Force NESlib RLE'
            TabOrder = 2
          end
        end
        object GroupBox11: TGroupBox
          Left = 135
          Top = 3
          Width = 112
          Height = 80
          Caption = 'Palette to clipboard'
          TabOrder = 4
          object CheckExportPalFilename: TCheckBox
            Left = 11
            Top = 16
            Width = 97
            Height = 17
            Caption = 'Filename in label'
            TabOrder = 0
          end
          object CheckExportPalSet: TCheckBox
            Left = 11
            Top = 32
            Width = 97
            Height = 17
            Caption = 'Set # in label'
            TabOrder = 1
          end
        end
        object GroupBox14: TGroupBox
          Left = 3
          Top = 82
          Width = 129
          Height = 42
          Caption = 'Asm syntax: signage'
          TabOrder = 5
          object RadioAsmCaSign: TRadioButton
            Left = 6
            Top = 16
            Width = 63
            Height = 17
            Caption = 'ca65: <-'
            Font.Charset = DEFAULT_CHARSET
            Font.Color = clWindowText
            Font.Height = -11
            Font.Name = 'Tahoma'
            Font.Style = []
            ParentFont = False
            TabOrder = 0
          end
          object RadioAsmOtherSign: TRadioButton
            Left = 70
            Top = 16
            Width = 56
            Height = 17
            Caption = 'other: -'
            Font.Charset = DEFAULT_CHARSET
            Font.Color = clWindowText
            Font.Height = -11
            Font.Name = 'Tahoma'
            Font.Style = []
            ParentFont = False
            TabOrder = 1
          end
        end
        object GroupBox16: TGroupBox
          Left = 135
          Top = 82
          Width = 112
          Height = 42
          Caption = 'Animation data as'
          TabOrder = 6
          object RadioAnimAsTable: TRadioButton
            Left = 11
            Top = 16
            Width = 48
            Height = 17
            Caption = 'table'
            TabOrder = 0
          end
          object RadioAnimAsFooter: TRadioButton
            Left = 58
            Top = 16
            Width = 48
            Height = 17
            Caption = 'footer'
            TabOrder = 1
          end
        end
        object GroupBox17: TGroupBox
          Left = 108
          Top = 124
          Width = 139
          Height = 80
          Caption = 'Animation format'
          TabOrder = 7
          object Radio6bit: TRadioButton
            Left = 8
            Top = 16
            Width = 126
            Height = 17
            Caption = '2 bit tags, 6 bit time'
            TabOrder = 0
          end
          object Radio8bit: TRadioButton
            Left = 8
            Top = 32
            Width = 128
            Height = 17
            Caption = '8 bit tags, 8 bit time'
            TabOrder = 1
          end
          object Radio14bit: TRadioButton
            Left = 8
            Top = 48
            Width = 128
            Height = 17
            Caption = '2 bit tags, 14 bit time'
            TabOrder = 2
          end
        end
      end
      object TabSheetBitmapExport: TTabSheet
        Caption = 'Export Image'
        object GroupBox19: TGroupBox
          Left = 3
          Top = 3
          Width = 180
          Height = 56
          Caption = 'Default image export format'
          TabOrder = 0
          object RadioExportDefaultPNG: TRadioButton
            Left = 6
            Top = 16
            Width = 113
            Height = 17
            Caption = 'PNG-8 (.png)'
            TabOrder = 0
          end
          object RadioExportDefaultBMP: TRadioButton
            Left = 6
            Top = 32
            Width = 170
            Height = 17
            Caption = 'Bitmap; 4bit if possible (.bmp)'
            TabOrder = 1
          end
        end
        object GroupBox20: TGroupBox
          Left = 183
          Top = 3
          Width = 224
          Height = 56
          Caption = 'Re-importable colour table extras (PNG-8)'
          TabOrder = 2
          object CheckExportIncludeNonactiveSupbals: TCheckBox
            Left = 6
            Top = 16
            Width = 212
            Height = 17
            Caption = 'Include the 3 nonactive subpalette sets'
            TabOrder = 0
          end
          object CheckExportIncludeSystemLUT: TCheckBox
            Left = 6
            Top = 32
            Width = 212
            Height = 17
            Caption = 'Include system palette'
            TabOrder = 1
          end
        end
        object GroupBox21: TGroupBox
          Left = 3
          Top = 60
          Width = 404
          Height = 54
          Caption = 'When a system palette is put in a colour LUT, arrange it...'
          TabOrder = 1
          object RadioExportVerticalSystemLUT: TRadioButton
            Left = 6
            Top = 16
            Width = 360
            Height = 17
            Caption = 'Vertically (looks nice in Aseprite when using 4 colour columns)'
            TabOrder = 0
          end
          object RadioExportHorizontalSystemLUT: TRadioButton
            Left = 6
            Top = 32
            Width = 360
            Height = 17
            Caption = 
              'Horizontally (looks nice in Adobe Color Table; preserves index o' +
              'rder)'
            TabOrder = 1
          end
        end
        object GroupBox24: TGroupBox
          Left = 3
          Top = 114
          Width = 538
          Height = 70
          Caption = 
            'Full subpalette (16-colour) non-sprite exports: Treat common col' +
            'our....'
          TabOrder = 3
          object RadioExport16_normal: TRadioButton
            Left = 6
            Top = 16
            Width = 520
            Height = 17
            Caption = 
              'Normally (Each attribute puts down its own common colour copy. G' +
              'ood for attribute to layer operations)'
            TabOrder = 0
          end
          object RadioExport16_0: TRadioButton
            Left = 6
            Top = 32
            Width = 460
            Height = 17
            Caption = 
              'Force to 0 (May be good for editing more cleanily in general pur' +
              'pose pixel art tools)'
            TabOrder = 1
          end
          object RadioExport16_1: TRadioButton
            Left = 6
            Top = 48
            Width = 524
            Height = 17
            Caption = 
              'Force to 0 of 2nd subpalette (effectively like "force to 0" but ' +
              'avoids Aseprite treating 0 as transparent)'
            TabOrder = 2
          end
        end
        object GroupBox25: TGroupBox
          Left = 3
          Top = 186
          Width = 538
          Height = 48
          Caption = 'Enable Slimmed subpalette exports (13 colours) for....'
          TabOrder = 4
          object CheckExport13Col: TCheckBox
            Left = 90
            Top = 20
            Width = 84
            Height = 17
            Caption = 'Backgrounds'
            TabOrder = 0
          end
          object CheckExport13ColSpr: TCheckBox
            Left = 184
            Top = 20
            Width = 84
            Height = 17
            Caption = 'Meta-Sprites'
            TabOrder = 1
          end
          object CheckExport13ColTiles: TCheckBox
            Left = 11
            Top = 20
            Width = 60
            Height = 17
            Caption = 'Tilesets'
            TabOrder = 2
          end
          object CheckExport13ColMTiles: TCheckBox
            Left = 280
            Top = 20
            Width = 74
            Height = 17
            Caption = 'Meta-Tiles'
            TabOrder = 3
          end
          object CheckExport13ColSubpals: TCheckBox
            Left = 360
            Top = 20
            Width = 100
            Height = 17
            Caption = 'Subpalettes'
            TabOrder = 4
          end
        end
      end
      object TabSheet5: TTabSheet
        Caption = 'Grids and guides'
        ImageIndex = 4
        object GroupBox4: TGroupBox
          Left = 3
          Top = 3
          Width = 126
          Height = 39
          Caption = 'Autoshow grid when'
          TabOrder = 0
          object CheckAutoshowDrag: TCheckBox
            Left = 11
            Top = 16
            Width = 112
            Height = 17
            Caption = 'dragging content'
            TabOrder = 0
          end
        end
        object GroupBox5: TGroupBox
          Left = 144
          Top = 44
          Width = 262
          Height = 84
          Caption = 'Metasprite warnings'
          TabOrder = 1
          object CheckMsprYellow: TCheckBox
            Left = 11
            Top = 16
            Width = 248
            Height = 17
            Caption = 'Yellow: Just 1 of this metasprite fits at scanline'
            TabOrder = 0
          end
          object CheckMsprOrange: TCheckBox
            Left = 11
            Top = 32
            Width = 237
            Height = 17
            Caption = 'Orange: Metasprite is at scanline limit (8)'
            TabOrder = 1
          end
          object CheckMsprRed: TCheckBox
            Left = 11
            Top = 48
            Width = 230
            Height = 17
            Caption = 'Red: This metasprite alone causes flicker'
            TabOrder = 2
          end
          object CheckMsprCyan: TCheckBox
            Left = 11
            Top = 64
            Width = 240
            Height = 17
            Caption = 'Cyan: A warning indicator of custom threshold'
            TabOrder = 3
          end
        end
        object GroupBox6: TGroupBox
          Left = 144
          Top = 130
          Width = 128
          Height = 95
          Caption = '32x30 grid: Navigator'
          TabOrder = 2
          object RadioNavScrAlways: TRadioButton
            Left = 11
            Top = 14
            Width = 66
            Height = 17
            Caption = 'Always'
            TabOrder = 0
          end
          object RadioNavScrMouse: TRadioButton
            Left = 11
            Top = 29
            Width = 77
            Height = 17
            Caption = 'Mouse over'
            TabOrder = 1
          end
          object RadioNavScrMB: TRadioButton
            Left = 11
            Top = 44
            Width = 113
            Height = 17
            Caption = 'M. over / Button'
            TabOrder = 2
          end
          object RadioNavScrButton: TRadioButton
            Left = 11
            Top = 59
            Width = 113
            Height = 17
            Caption = 'Button down'
            TabOrder = 3
          end
          object RadioNavScrNever: TRadioButton
            Left = 11
            Top = 74
            Width = 113
            Height = 17
            Caption = 'Never'
            TabOrder = 4
          end
        end
        object GroupBox7: TGroupBox
          Left = 278
          Top = 130
          Width = 128
          Height = 95
          Caption = '32x30 grid: main canvas'
          TabOrder = 3
          object RadioMainScrAlways: TRadioButton
            Left = 11
            Top = 14
            Width = 113
            Height = 17
            Caption = 'Always'
            TabOrder = 0
          end
          object RadioMainScrMouse: TRadioButton
            Left = 11
            Top = 29
            Width = 113
            Height = 17
            Caption = 'Mouse over'
            TabOrder = 1
          end
          object RadioMainScrMB: TRadioButton
            Left = 11
            Top = 44
            Width = 113
            Height = 17
            Caption = 'M. over / Button'
            TabOrder = 2
          end
          object RadioMainScrButton: TRadioButton
            Left = 11
            Top = 59
            Width = 113
            Height = 17
            Caption = 'Button down'
            TabOrder = 3
          end
          object RadioMainScrNever: TRadioButton
            Left = 11
            Top = 74
            Width = 113
            Height = 17
            Caption = 'Never'
            TabOrder = 4
          end
        end
      end
      object TabSheet6: TTabSheet
        Caption = 'Workspace'
        ImageIndex = 5
        object RGroupWorkspace: TGroupBox
          Left = 151
          Top = 3
          Width = 128
          Height = 52
          Caption = 'Workspace: Metasprites'
          TabOrder = 0
          object RadioSprlistLeft: TRadioButton
            Left = 11
            Top = 16
            Width = 82
            Height = 17
            Caption = 'Spritelist: left'
            TabOrder = 1
          end
          object RadioSprlistCenter: TRadioButton
            Left = 11
            Top = 31
            Width = 98
            Height = 17
            Caption = 'Spritelist: center'
            TabOrder = 0
          end
        end
        object GroupBox2: TGroupBox
          Left = 281
          Top = 3
          Width = 128
          Height = 52
          Caption = 'Workspace: Tile Editor'
          TabOrder = 1
          object RadioToolTop: TRadioButton
            Left = 11
            Top = 16
            Width = 113
            Height = 17
            Caption = 'Toolbar: top'
            TabOrder = 0
          end
          object RadioToolBottom: TRadioButton
            Left = 11
            Top = 32
            Width = 113
            Height = 17
            Caption = 'Toolbar: bottom'
            TabOrder = 1
          end
        end
        object GroupBox8: TGroupBox
          Left = 3
          Top = 3
          Width = 142
          Height = 37
          Caption = 'Snap'
          TabOrder = 2
          object CheckFormToMonitor: TCheckBox
            Left = 11
            Top = 16
            Width = 128
            Height = 17
            Caption = 'Forms to Monitor edge'
            TabOrder = 0
          end
        end
        object GroupBox9: TGroupBox
          Left = 151
          Top = 57
          Width = 255
          Height = 52
          Caption = 'Lightbox mode: alpha value'
          TabOrder = 3
          object TrackBarAlpha: TTrackBar
            Left = 3
            Top = 17
            Width = 249
            Height = 27
            Max = 220
            Min = 140
            Frequency = 8
            Position = 180
            TabOrder = 0
            ThumbLength = 16
          end
        end
        object GroupBox10: TGroupBox
          Left = 3
          Top = 42
          Width = 142
          Height = 67
          Caption = 'Menu: open/save binaries'
          TabOrder = 4
          object RadioOpenSave1: TRadioButton
            Left = 11
            Top = 16
            Width = 113
            Height = 17
            Caption = 'in File menu (new)'
            TabOrder = 0
          end
          object RadioOpenSave2: TRadioButton
            Left = 11
            Top = 31
            Width = 128
            Height = 17
            Caption = 'in type menus (classic)'
            TabOrder = 1
          end
          object RadioOpenSave3: TRadioButton
            Left = 11
            Top = 46
            Width = 113
            Height = 17
            Caption = 'in both'
            TabOrder = 2
          end
        end
        object GroupBox12: TGroupBox
          Left = 3
          Top = 111
          Width = 142
          Height = 53
          Caption = 'Titlebar contents'
          TabOrder = 5
          object RadioFilename: TRadioButton
            Left = 11
            Top = 16
            Width = 113
            Height = 17
            Caption = 'filename'
            TabOrder = 0
          end
          object RadioFilenameFolder: TRadioButton
            Left = 11
            Top = 32
            Width = 105
            Height = 17
            Caption = 'filename + folder'
            TabOrder = 1
          end
          object RadioFullPath: TRadioButton
            Left = 76
            Top = 16
            Width = 60
            Height = 17
            Caption = 'full path'
            TabOrder = 2
          end
        end
        object GroupBox23: TGroupBox
          Left = 411
          Top = 3
          Width = 128
          Height = 52
          Caption = 'Workspace: Main editor'
          TabOrder = 6
          object RadioSidebarLeft: TRadioButton
            Left = 11
            Top = 16
            Width = 113
            Height = 17
            Caption = 'Sidebar: left'
            TabOrder = 0
          end
          object RadioSidebarRight: TRadioButton
            Left = 11
            Top = 32
            Width = 113
            Height = 17
            Caption = 'Sidebar: right'
            TabOrder = 1
          end
        end
      end
    end
  end
  object Panel2: TPanel
    Left = 0
    Top = 280
    Width = 563
    Height = 34
    Align = alBottom
    BevelOuter = bvNone
    ParentColor = True
    TabOrder = 0
    object OKBtn: TButton
      Left = 382
      Top = 2
      Width = 94
      Height = 25
      Caption = 'Apply and save'
      Default = True
      ModalResult = 1
      TabOrder = 0
      OnClick = OKBtnClick
    end
    object CancelBtn: TButton
      Left = 482
      Top = 2
      Width = 75
      Height = 25
      Cancel = True
      Caption = 'Cancel'
      ModalResult = 2
      TabOrder = 2
    end
    object HelpBtn: TButton
      Left = 5
      Top = 2
      Width = 123
      Height = 25
      Caption = '&Reload install settings'
      TabOrder = 1
      OnClick = HelpBtnClick
    end
  end
end
