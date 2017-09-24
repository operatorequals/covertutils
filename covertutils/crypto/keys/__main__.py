
from covertutils.crypto.keys import *
from covertutils.crypto.algorithms import *

import binascii, base64, sys

algo_dict = {
		'null' : NullCyclingAlgorithm,
		'std' : StandardCyclingAlgorithm,
		'crc' : Crc32CyclingAlgorithm,
	}

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("key_type", help = 'The algorithm name to use', choices = algo_dict.keys(), type = str, default = 'std' )
parser.add_argument("passphrase", help = "The passphrase for key generation", type = str)
parser.add_argument("message", help = "The message to be encrypted [use '-' for stdin]", type = str, default = '-')

parser.add_argument('--decrypt', '-d', help = 'Add if the message is in encrypted form', action = 'store_true', default = False, )
parser.add_argument('--input-type', '-i', help = 'Specify the form of the input', choices = ['b64', 'hex', 'plain'], default = 'plain')
parser.add_argument('--output-type', '-o', help = 'Specify the form of the ouput', choices = ['b64', 'hex', 'plain'], default = 'plain')

args = parser.parse_args()
# print args
algo = algo_dict[args.key_type]

key = StandardCyclingKey(args.passphrase, cycling_algorithm = algo)

func = key.encrypt
if args.decrypt :
	func = key.decrypt

if args.message == '-' :
	args.message = sys.stdin.read()

if args.input_type == 'hex' :
	message = str(binascii.unhexlify(args.message))
elif args.input_type == 'b64' :
	message = base64.b64decode(args.message)
else :
	message = args.message

res = func(message)

if args.output_type == 'hex' :
	res = binascii.hexlify(res)
if args.output_type == 'b64' :
	res = base64.b64encode(res)

print (str(res))
