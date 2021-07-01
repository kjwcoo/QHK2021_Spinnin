"""
Zurich Instruments LabOne Python API Example

Demonstrate how to connect to a Zurich Instruments Arbitrary Waveform Generator
and compile/upload an AWG program to the instrument.
"""

# Copyright 2018 Zurich Instruments AG

import time
import textwrap
import os
import zhinst.utils

import json

def generate_source_file( ):
    # Read the instruction set from Qobj
    with open( 'local_exp.txt', 'r' ) as file:
        result = json.loads('[' + file.read() + ']')
    print( result )
    playCode = "wave complete_cycle = join( sudden_start, ramp_start"
    newCode = ""
    for val, dict in enumerate( result[ 0 ] ):
        print( val )
        if dict[ 'name' ] == 'x':
            gateCode = "wave x_" + str( val ) + " = A_base + A * sine( N, A, 0, nPeriod );\n" 
            playCode = playCode + ", x_" + str( val )
        elif dict[ 'name' ] == 'y':
            gateCode = "wave y_" + str( val )+ " = A_base + A * cosine( N, A, 0, nPeriod );\n" 
            playCode = playCode + ", y_" + str( val )
        elif dict[ 'name' ] == 'id':
            gateCode = "wave id_" + str( val )+ " = A_base + 0.0 * sine( N, 0.0, 0, nPeriod );\n" 
            playCode = playCode + ", id_" + str( val )
        else:
            break
        newCode = newCode + gateCode
    playCode = playCode + ", ramp_end, sudden_end );\n"
    newCode = newCode + playCode + "playWave( complete_cycle );"
    code = """
              const N_sudden = 100;
              const A_sudden = 0.3;
              const N_ramp = 1000;
              const A_ramp = 0.6;
              const N = 1000;
              const A_base = 0.6;
              const A = 0.2;
              const nPeriod = 30;
              wave sudden_start = ramp( N_sudden, 0.0, A_sudden );
              wave ramp_start = ramp( N_ramp, A_sudden, A_ramp );
              wave ramp_end = ramp( N_ramp, A_ramp, A_sudden );
              wave sudden_end = ramp( N_sudden, A_sudden, 0.0 );
              {str0}
              """.format( str0 = newCode )
    print( code )
    SOURCE = textwrap.dedent(
       code
    )
    return SOURCE

def run_example(device_id, awg_sourcefile=None):
    # Settings
    apilevel_example = 6  # The API level supported by this example.
    err_msg = "This example can only be ran on either an HDAWG with the AWG option enabled."
    # Call a zhinst utility function that returns:
    # - an API session `daq` in order to communicate with devices via the data server.
    # - the device ID string that specifies the device branch in the server's node hierarchy.
    # - the device's discovery properties.
    (daq, device, _) = zhinst.utils.create_api_session(
        device_id, apilevel_example, required_devtype="HDAWG", required_err_msg=err_msg
    )
    zhinst.utils.api_server_version_check(daq)

    # Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
    zhinst.utils.disable_everything(daq, device)

    # 'system/awg/channelgrouping' : Configure how many independent sequencers
    #   should run on the AWG and how the outputs are grouped by sequencer.
    #   0 : 4x2 with HDAWG8; 2x2 with HDAWG4.
    #   1 : 2x4 with HDAWG8; 1x4 with HDAWG4.
    #   2 : 1x8 with HDAWG8.
    # Configure the HDAWG to use one sequencer with the same waveform on all output channels.
    daq.setInt(f"/{device}/system/awg/channelgrouping", 1)

    # Create an instance of the AWG Module
    awgModule = daq.awgModule()
    awgModule.set("device", device)
    awgModule.execute()

    # Get the LabOne user data directory (this is read-only).
    data_dir = awgModule.getString("directory")
    # The AWG Tab in the LabOne UI also uses this directory for AWG seqc files.
    src_dir = os.path.join(data_dir, "awg", "src")
    if not os.path.isdir(src_dir):
        # The data directory is created by the AWG module and should always exist. If this exception is raised,
        # something might be wrong with the file system.
        raise Exception(f"AWG module wave directory {src_dir} does not exist or is not a directory")

    # Note, the AWG source file must be located in the AWG source directory of the user's LabOne data directory.
    if awg_sourcefile is None:
        # Write an AWG source file to disk that we can compile in this example.
        awg_sourcefile = "ziPython_example_awg_sourcefile.seqc"
        SOURCE = generate_source_file()
        with open(os.path.join(src_dir, awg_sourcefile), "w") as f:
            f.write(SOURCE)
    else:
        if not os.path.exists(os.path.join(src_dir, awg_sourcefile)):
            raise Exception(
                f"The file {awg_sourcefile} does not exist, this must be specified via an absolute or relative path."
            )

    print("Will compile and load", awg_sourcefile, "from", src_dir)

    # Transfer the AWG sequence program. Compilation starts automatically.
    awgModule.set("compiler/sourcefile", awg_sourcefile)
    # Note: when using an AWG program from a source file (and only then), the compiler needs to
    # be started explicitly:
    awgModule.set("compiler/start", 1)
    timeout = 20
    t0 = time.time()
    while awgModule.getInt("compiler/status") == -1:
        time.sleep(0.1)
        if time.time() - t0 > timeout:
            Exception("Timeout")

    if awgModule.getInt("compiler/status") == 1:
        # compilation failed, raise an exception
        raise Exception(awgModule.getString("compiler/statusstring"))
    if awgModule.getInt("compiler/status") == 0:
        print("Compilation successful with no warnings, will upload the program to the instrument.")
    if awgModule.getInt("compiler/status") == 2:
        print("Compilation successful with warnings, will upload the program to the instrument.")
        print("Compiler warning: ", awgModule.getString("compiler/statusstring"))

    # Wait for the waveform upload to finish
    time.sleep(0.2)
    i = 0
    while (awgModule.getDouble("progress") < 1.0) and (awgModule.getInt("elf/status") != 1):
        print(f"{i} progress: {awgModule.getDouble('progress'):.2f}")
        time.sleep(0.5)
        i += 1
    print(f"{i} progress: {awgModule.getDouble('progress'):.2f}")
    if awgModule.getInt("elf/status") == 0:
        print("Upload to the instrument successful.")
    if awgModule.getInt("elf/status") == 1:
        raise Exception("Upload to the instrument failed.")

    print("Success. Enabling the AWG.")
    # This is the preferred method of using the AWG: Run in single mode continuous waveform playback is best achieved by
    # using an infinite loop (e.g., while (true)) in the sequencer program.
    daq.setInt(f"/{device}/awgs/0/single", 1)
    daq.setInt(f"/{device}/awgs/0/enable", 1)

result = run_example( 'dev8189', )