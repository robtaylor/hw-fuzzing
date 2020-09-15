#!/usr/bin/python3
# TODO(ttrippel): add license
"""This is a cocotb testbench harness to interface with afl-fuzz.

Description:
The testbench starts by reseting the DUT for a duration of DUT_RESET_DURATION_NS
nanoseconds. After reset, the testbench reads bytes from STDIN and feeds them to
the input port(s) of the DUT. The testbench proceeds until there are no inputs
more inputs to provide the DUT.

Assertions:

Environment Vars:
Since cocotb does not support passing arguments to the tests implemented in
Python, any arguments must be passed as environment variables.
"""

import logging
import math
import os
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# Import custom cocotb extension packages
sys.path.append("/Users/ttrippel/repos/hw-fuzzing/hw/tb")
from cocotb_ext.drivers.tlul import TLULHost

CLK_PERIOD_NS = 10  # duration of simulation clock period
DUT_RESET_DURATION_NS = 50  # duration to hold DUT in reset for in ns


class RVTimerTB():
  def __init__(self, dut, debug=False):
    self.dut = dut
    self.tlul = TLULHost(dut, "", dut.clk_i)

    # Set verbosity on our various interfaces
    level = logging.DEBUG if debug else logging.WARNING
    # self.afl_in.log.setLevel(level)
    self.dut._log.setLevel(level)

    # Create a scoreboard

  async def reset(self, duration_ns):
    self.dut._log.debug("Resetting the DUT ...")
    self.dut.rst_ni <= 0
    # self.afl_in.bus.valid <= 0
    await Timer(duration_ns, units="ns")
    await RisingEdge(self.dut.clk_i)
    self.dut.rst_ni <= 1
    self.dut._log.debug("Reset complete!")


@cocotb.test()
async def rv_timer_tb(dut):
  """Reads transactions from STDIN (generated by AFL) to fuzz the DUT.

  Args:
    dut: The object representing the DUT being simulated.

  Required Environment Vars:
    INPUT_WIDTH: The width (in # of bits) of the input port.

  Returns:
    None

  Raises:
    AssertionError: ...
  """

  # Get test parameters
  input_size_bits = int(os.getenv("INPUT_WIDTH"))
  input_size_bytes = math.ceil(input_size_bits / 8)
  dut._log.info(f"Input Port Size: {input_size_bytes}")

  # Instantiate TB
  tb = RVTimerTB(dut)

  # Create and start the clock
  clock = Clock(dut.clk_i, CLK_PERIOD_NS, units="ns")
  cocotb.fork(clock.start())

  # Reset the DUT
  await tb.reset(DUT_RESET_DURATION_NS)

  # # Send in random input values
  # dut_input_bytes = sys.stdin.buffer.read(input_size_bytes)
  # while dut_input_bytes:
  # dut_input_int = int.from_bytes(dut_input_bytes,
  # byteorder="big",
  # signed=False)
  # dut._log.info("Setting code to:")
  # dut._log.info(f"  (bytes): {dut_input_bytes.hex()}")
  # dut._log.info(f"  (int):   {dut_input_int}")
  # dut.code <= dut_input_int
  # await FallingEdge(dut.clk)
  # dut._log.info(f" Code: {dut.code.value.binstr}")
  # dut._log.info(f" State: {dut.state.value.integer}")

  # # Check we unlocked the lock
  # assert dut.unlocked.value.integer == 0, "REACHED FINAL STATE!"

  # # read next input
  # dut_input_bytes = sys.stdin.buffer.read(input_size_bytes)
