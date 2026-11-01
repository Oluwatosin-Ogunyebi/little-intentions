$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$out = Join-Path $root 'artifacts/orbit'
$source = [Drawing.Image]::FromFile((Join-Path $root 'assets/orbit/source/orbit-spritesheet.png'))
$sheet = New-Object Drawing.Bitmap 960,240
$g = [Drawing.Graphics]::FromImage($sheet)
$g.Clear([Drawing.Color]::FromArgb(22,34,42))
$font = New-Object Drawing.Font 'Arial',12
$refs = @(@(0,0,'Neutral'),@(1,2,'Run right'),@(2,2,'Run left'),@(6,0,'Waiting'),@(4,1,'Jump'))
for ($i=0; $i -lt $refs.Count; $i++) {
    $r=$refs[$i]
    $src=New-Object Drawing.Rectangle ($r[1]*192),($r[0]*208),192,208
    $dst=New-Object Drawing.Rectangle ($i*192),0,192,208
    $g.DrawImage($source,$dst,$src,[Drawing.GraphicsUnit]::Pixel)
    $g.DrawString($r[2],$font,[Drawing.Brushes]::White,($i*192+12),212)
}
$sheet.Save((Join-Path $out 'source-reference.png'),[Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$sheet.Dispose();$source.Dispose()
foreach ($clip in @('walk','ask_wait','interact','celebrate')) {
    $sheet=New-Object Drawing.Bitmap 960,520
    $g=[Drawing.Graphics]::FromImage($sheet)
    $g.Clear([Drawing.Color]::FromArgb(22,34,42))
    for ($i=0;$i -lt 8;$i++) {
        $img=[Drawing.Image]::FromFile((Join-Path $out "$clip-$i.png"))
        $x=($i%4)*240;$y=[math]::Floor($i/4)*260
        $g.DrawImage($img,[int]$x,[int]$y,240,240)
        $g.DrawString("$clip | phase $i/8",$font,[Drawing.Brushes]::White,[int]($x+10),[int]($y+240))
        $img.Dispose()
    }
    $sheet.Save((Join-Path $out "$clip-contact-sheet.png"),[Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose();$sheet.Dispose()
}
$font.Dispose()
