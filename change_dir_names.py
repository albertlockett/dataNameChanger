# Script to change all the names of files in a directory.
#
# Note, doesn't actually delete the old files.
#
# Usage:
# change_dir <root_in> ([-f <output_names>]) | ([-n <# files>] [-r]) | [-h]
#
# I suggest you run it in an otherwise empty directory, otherwise the split
# files will get all intermingled with your good files
# 
# Arguments
# -f = Generate filenames automatically from file
# -n = number of files to generate
# -r = randomly generate filenames
#
# Inputs
# output_names = File containing names of output file names
# # files      = Number of files to generate using -n flag
#
# HOW IT WORKS:
# It creates a tarball of the input directory you give it. Then it splits the
# tarball bytewise into a bunch of files. 
#
# The files are named either after the words it reads from a file (-f arguement)
# one filename per line, or it will generate -n files with numeric names, or use
# -r command to get random file names. Random filenames are 64 byte ascii strs
#
# The file size decreases as it moves away from the start of the tarball, so for
# example if I ls -al the output of this:
#
# -rw-rw-r-- 1 albert albert  514 Jun 17 10:24 0
# -rw-rw-r-- 1 albert albert  515 Jun 17 10:24 2
# -rw-rw-r-- 1 albert albert  513 Jun 17 10:24 1
#
# Note that the last file in the split will be biggest. The file size is import-
# tant because it is how the file gets reconstructed. 
#
# TODO:
# - Check negative file sizes
# - Handle file-size errors more gracefully
#
#
# Albert Lockett
# June 2014

import os
import sys
import getopt
import string
import random

def id_generator(size=64, chars=string.ascii_uppercase + string.digits):
  random_filename = ''.join(random.choice(chars) for _ in range(size))
  return random_filename

def main(argv):

	# If root directory not given, exit
  if(len(argv) < 1):
    print('no root dir specified, use -h for help')
    sys.exit(-1)

  if not os.path.isdir(argv[0]):
    print('invalid directory given as arguement 0\nexitting')
    sys.exit(-1)

  # TODO: Check here if root dir is valid directory
  root_dir = argv[0]

  # list of variables for flow control
  f_flag_given = False
  genrator_filename = ''
  n_flag_given = False
  num_of_files = 0
  r_flag_given = False

	# Parse command line arguements
  try:
    opts, args = getopt.getopt(argv[1:], "f:n:rh",
    ["file_names=","num_files="])
  except getopt.GetoptError :
    print 'getopt Error exit -1'
    sys.exit(-1)

  for opt, arg in opts:
    if opt == '-h':
      print('\n-- Change Dir Program --\n')
      print('usage: python chage_dir_names.py ' 
      	'<root_in> ([-f <output_names>]) | ([-n <# files>] [-r]) | [-h]')
      print('\nArguments')
      print(' -f = Generate filenames automatically from file')
      print(' -n = number of files to generate')
      print(' -r = randomly generate filenames')
      print(' -h = help')
      print('\nInputs')
      print(' output_names = File containing names of output file names')
      print(' # files      = Number of files to generate using -n flag')
      print('\nSuggestion: run this in an otherwise empty directory')
      print('')
    if opt in ('-f','--file_names'):
      f_flag_given = True
      generator_filename = arg
    if opt in ('-n','--num_files'):
      n_flag_given = True
      num_of_files = int(arg)
    if opt == '-r':
      r_flag_given = True
	
  # Check that both n flag and f flag are not given
  if n_flag_given and f_flag_given:
  	print 'must not provide both n arguement and f arguement'
  	print 'use: python change_dir_names.py -h for help'
  	sys.exit(-1)


	# Default behaviour
  if not n_flag_given and not f_flag_given:
    print('Default behaviour selected')
    n_flag_given = True
    num_of_files = 10

	# Tarball input directory
  tar_cmd = 'tar -zcvf tmp.tar '+root_dir
  os.system(tar_cmd)
  print '### REMEMBER TO UNCOMMENT THE TAR COMMAND TO RUN THIS FOR REAL ###'

  # Open the tarball, prepare to split
  tar = open("tmp.tar", "rb")

	# generate list of file names
  print('Generating File names')
  file_names = []
  if f_flag_given:
    print('Reading filenames from: '+generator_filename)
    f = open(generator_filename)
    file_names = [l.rstrip() for l in f.readlines()]

  if n_flag_given:
    print('Numeric file creation selected ')
    print('Number of files = ' + str(num_of_files))
    sys.stdout.write('File naming scheme:')
    if(r_flag_given):
      print(' random')
    else:
      print(' numeric')

    for i in range(0,num_of_files):
      if r_flag_given:
        # TODO: Randomly generate file here
        file_names.append(id_generator())
      else:
        file_names.append(str(i))

  # Generate list of file sizes
  file_sizes = []
  file_size = os.stat('tmp.tar').st_size
  bytes_per_file = file_size / len(file_names)
  for i in range(0, len(file_names[:-1])):
    file_sizes.append(bytes_per_file - i)

  # QA check file_sizes
  if file_size - sum(file_sizes) in file_sizes:
    # Last file will be same size as another file, cannot untar 
    # TODO: Handle error
    print("There was a problem, I'm so sorry ... ")
    print('TODO: albert handle file size error, exitting!')
    sys.exit(-1)
  if file_size - sum(file_sizes) < max(file_sizes):
    # last filesize is too small, exit 
    # TODO: Handle error
    print(file_sizes)
    print("There was a problem, I'm so sorry ... ")
    print('TODO: albert handle file size error, exitting!')
    sys.exit(-1)


  # Write bytes to individual files
  for file_num in range(0,len(file_names) - 1):

    print("Writing file #"+str(file_num)+" - "+file_names[file_num])

    f = open(file_names[file_num], "wb")
    byte_arr = []
    try:
      for byte_num in range (0, file_sizes[file_num]):
        byte_arr.append(tar.read(1))
      f.write(bytearray(byte_arr))
    finally:
      f.close()

  # Write last file
  byte_arr = []
  byte = tar.read(1)
  while byte != "":
    byte_arr.append(byte)
    byte = tar.read(1)
  f = open(file_names[-1], "wb")
  f.write(bytearray(byte_arr))
  f.close()

  # Close the tar
  tar.close()

  # Cleanup
  os.system("rm tmp.tar")

if __name__ == '__main__':
  main(sys.argv[1:])
  print('')