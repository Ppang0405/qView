#!/usr/bin/env pwsh

param
(
    [switch]$CI,
    $Prefix = "/usr"
)

$qtVersion = [version](qmake -query QT_VERSION)
Write-Host "Detected Qt version $qtVersion"

if ($IsWindows) {
    dist/scripts/vcvars.ps1
} elseif ($IsMacOS) {
    # By default CMake sets the deployment target for macOS to the build machine's version; set
    # it explicitly to the version supported by Qt for compatibility with older macOS versions
    $env:MACOSX_DEPLOYMENT_TARGET = (Select-String -Path (Join-Path $env:QT_ROOT_DIR 'mkspecs/qconfig.pri'), (Join-Path $env:QT_ROOT_DIR 'mkspecs/common/macx.conf') -Pattern '^\s*QMAKE_MACOSX_DEPLOYMENT_TARGET\s*=\s*(.+?)\s*$').Matches[0].Groups[1].Value
}

# Prepare CMake arguments. Swift requires the Ninja generator.
$cmakeArgs = @(
    "-G", "Ninja",
    "-DCMAKE_BUILD_TYPE=Release",
    "-DCMAKE_INSTALL_PREFIX=$Prefix"
)

if ($env:nightlyDefines) {
    $cmakeArgs += "-D$($env:nightlyDefines)"
}

# Swift's generated C++ header must be compiled by Clang, so on Linux and Windows use the
# Clang that ships with the Swift toolchain (on macOS, Xcode's Clang already matches)
if (-not $IsMacOS) {
    $swiftc = Get-Item (Get-Command swiftc).Source
    $swiftBinDir = Split-Path ($swiftc.LinkTarget ? $swiftc.ResolvedTarget : $swiftc.FullName)
}
if ($IsWindows) {
    $cmakeArgs += "-DCMAKE_CXX_COMPILER=$(Join-Path $swiftBinDir 'clang-cl.exe')"
    # Workaround for https://developercommunity.visualstudio.com/t/10664660
    $cmakeArgs += '-DCMAKE_CXX_FLAGS=-D_DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR'
    # vcvars selects the target libraries; the compilers need the target triple as well
    if ($env:buildArch -eq 'X86') {
        $cmakeArgs += "-DCMAKE_CXX_COMPILER_TARGET=i686-pc-windows-msvc"
        $cmakeArgs += "-DCMAKE_Swift_COMPILER_TARGET=i686-unknown-windows-msvc"
    } elseif ($env:buildArch -eq 'Arm64') {
        $cmakeArgs += "-DCMAKE_CXX_COMPILER_TARGET=aarch64-pc-windows-msvc"
        $cmakeArgs += "-DCMAKE_Swift_COMPILER_TARGET=aarch64-unknown-windows-msvc"
    }
} elseif (-not $IsMacOS) {
    $cmakeArgs += "-DCMAKE_CXX_COMPILER=$(Join-Path $swiftBinDir 'clang++')"
}

function Build-QView([string]$BuildDir, [string[]]$ExtraArgs = @()) {
    cmake -B $BuildDir @cmakeArgs @ExtraArgs
    if ($LASTEXITCODE -ne 0) { throw "CMake configure failed" }
    cmake --build $BuildDir --parallel
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }
}

if ($IsMacOS -and $env:buildArch -eq 'Universal') {
    # Swift builds one architecture at a time, so build each and merge them with lipo
    Build-QView "build-arm64" @("-DCMAKE_OSX_ARCHITECTURES=arm64")
    Build-QView "build-x86_64" @("-DCMAKE_OSX_ARCHITECTURES=x86_64")
    Remove-Item -Recurse -Force "build/qView.app" -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path build | Out-Null
    Copy-Item -Path "build-arm64/qView.app" -Destination "build/qView.app" -Recurse
    lipo -create "build-arm64/qView.app/Contents/MacOS/qView" "build-x86_64/qView.app/Contents/MacOS/qView" -output "build/qView.app/Contents/MacOS/qView"
    if ($LASTEXITCODE -ne 0) { throw "lipo failed" }
} elseif ($IsMacOS -and $env:buildArch) {
    $arch = $env:buildArch -eq 'X64' ? 'x86_64' : 'arm64'
    Build-QView "build" @("-DCMAKE_OSX_ARCHITECTURES=$arch")
} else {
    Build-QView "build"
}

# Copy artifact to bin directory for deployment scripts
New-Item -ItemType Directory -Force -Path bin
if ($IsWindows) {
    Copy-Item -Path "build/qView.exe" -Destination "bin/qView.exe" -Force
} elseif ($IsMacOS) {
    Copy-Item -Path "build/qView.app" -Destination "bin/qView.app" -Recurse -Force
} else {
    Copy-Item -Path "build/qview" -Destination "bin/qview" -Force
}
