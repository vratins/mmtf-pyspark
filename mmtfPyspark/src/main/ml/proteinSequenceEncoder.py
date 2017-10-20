'''
ProteinSequenceEncoder.py

Authorship information:
    __author__ = "Mars Huang"
    __maintainer__ = "Mars Huang"
    __email__ = "marshuang80@gmail.com:
    __status__ = "Done"
'''

from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
from pyspark.ml.linalg import VectorUDT


class proteinSequenceEncoder(object):
    '''
    This class encodes a protein sequence into a feature vector.
    The protein sequence must be present in the input data set,
    the default column name is "sequence". The default column name
    for the feature vector is "features".
    '''

    AMINO_ACIDS21 = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', \
                     'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y']

    properties = {
        'A' : [1.28,0.05,1.00,0.31,6.11,0.42,0.23],
        'G' : [0.00,0.00,0.00,0.00,6.07,0.13,0.15],
        'V' : [3.67,0.14,3.00,1.22,6.02,0.27,0.49],
        'L' : [2.59,0.19,4.00,1.70,6.04,0.39,0.31],
        'I' : [4.19,0.19,4.00,1.80,6.04,0.30,0.45],
        'F' : [2.94,0.29,5.89,1.79,5.67,0.30,0.38],
        'Y' : [2.94,0.30,6.47,0.96,5.66,0.25,0.41],
        'W' : [3.21,0.41,8.08,2.25,5.94,0.32,0.42],
        'T' : [3.03,0.11,2.60,0.26,5.60,0.21,0.36],
        'S' : [1.31,0.06,1.60,-0.04,5.70,0.20,0.28],
        'A' : [2.34,0.29,6.13,-1.01,10.74,0.36,0.25],
        'K' : [1.89,0.22,4.77,-0.99,9.99,0.32,0.27],
        'H' : [2.99,0.23,4.66,0.13,7.69,0.27,0.30],
        'D' : [1.60,0.11,2.78,-0.77,2.95,0.25,0.20],
        'E' : [1.56,0.15,3.78,-0.64,3.09,0.42,0.21],
        'N' : [1.60,0.13,2.95,-0.60,6.52,0.21,0.22],
        'Q' : [1.56,0.18,3.95,-0.22,5.65,0.36,0.25],
        'M' : [2.35,0.22,4.43,1.23,5.71,0.38,0.32],
        'P' : [2.67,0.00,2.72,0.72,6.80,0.13,0.34],
        'C' : [1.77,0.13,2.43,1.54,6.35,0.17,0.41],
        'X' : [0.00,0.00,0.00,0.00,0.00,0.00,0.00],
    }

	# Source: https://ftp.ncbi.nih.gov/repository/blocks/unix/blosum/BLOSUM/blosum62.blast.new
    blosum62 = {
         #      A  R  N  D  C  Q  E  G  H  I  L  K  M  F  P  S  T  W  Y  V
        'A' : [ 4,-1,-2,-2, 0,-1,-1, 0,-2,-1,-1,-1,-1,-2,-1, 1, 0,-3,-2, 0],
        'R' : [-1, 5, 0,-2,-3, 1, 0,-2, 0,-3,-2, 2,-1,-3,-2,-1,-1,-3,-2,-3],
        'N' : [-2, 0, 6, 1,-3, 0, 0, 0, 1,-3,-3, 0,-2,-3,-2, 1, 0,-4,-2,-3],
        'D' : [-2,-2, 1, 6,-3, 0, 2,-1,-1,-3,-4,-1,-3,-3,-1, 0,-1,-4,-3,-3],
        'C' : [ 0,-3,-3,-3, 9,-3,-4,-3,-3,-1,-1,-3,-1,-2,-3,-1,-1,-2,-2,-1],
        'Q' : [-1, 1, 0, 0,-3, 5, 2,-2, 0,-3,-2, 1, 0,-3,-1, 0,-1,-2,-1,-2],
        'E' : [-1, 0, 0, 2,-4, 2, 5,-2, 0,-3,-3, 1,-2,-3,-1, 0,-1,-3,-2,-2],
        'G' : [ 0,-2, 0,-1,-3,-2,-2, 6,-2,-4,-4,-2,-3,-3,-2, 0,-2,-2,-3,-3],
        'H' : [-2, 0, 1,-1,-3, 0, 0,-2, 8,-3,-3,-1,-2,-1,-2,-1,-2,-2, 2,-3],
        'I' : [-1,-3,-3,-3,-1,-3,-3,-4,-3, 4, 2,-3, 1, 0,-3,-2,-1,-3,-1, 3],
        'L' : [-1,-2,-3,-4,-1,-2,-3,-4,-3, 2, 4,-2, 2, 0,-3,-2,-1,-2,-1, 1],
        'K' : [-1, 2, 0,-1,-3, 1, 1,-2,-1,-3,-2, 5,-1,-3,-1, 0,-1,-3,-2,-2],
        'M' : [-1,-1,-2,-3,-1, 0,-2,-3,-2, 1, 2,-1, 5, 0,-2,-1,-1,-1,-1, 1],
        'F' : [-2,-3,-3,-3,-2,-3,-3,-3,-1, 0, 0,-3, 0, 6,-4,-2,-2, 1, 3,-1],
        'P' : [-1,-2,-2,-1,-3,-1,-1,-2,-2,-3,-3,-1,-2,-4, 7,-1,-1,-4,-3,-2],
        'S' : [ 1,-1, 1, 0,-1, 0, 0, 0,-1,-2,-2, 0,-1,-2,-1, 4, 1,-3,-2,-2],
        'T' : [ 0,-1, 0,-1,-1,-1,-1,-2,-2,-1,-1,-1,-1,-2,-1, 1, 5,-2,-2, 0],
        'W' : [-3,-3,-4,-4,-2,-2,-3,-2,-2,-3,-2,-3,-1, 1,-4,-3,-2,11, 2,-3],
        'Y' : [-2,-2,-2,-3,-2,-1,-2,-3, 2,-1,-1,-2,-1, 3,-3,-2,-2, 2, 7,-1],
        'V' : [ 0,-3,-3,-3,-1,-2,-2,-3,-3, 3, 1,-2, 1,-1,-2,-2, 0,-3,-1, 4],
        'X' : [-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4,-4],
    }


    def __init__(self, data, inputCol = "sequence", outputCol = "features"):

        self.data = data
        self.inputCol = inputCol
        self.outputCol = outputCol


    def oneHotEncode(self):
        '''
        One-hot encodes a protein sequence. The one-hot encoding
        encodes the 20 natural amino acids, plus X for any other
        residue for a total of 21 elements per residue.
        '''

        session = SparkSession.builder.getOrCreate()
        AMINO_ACIDS21 = self.AMINO_ACIDS21

        # Encoder function to be passed as User Defined Function (UDF)
        def encoder(s):

            values = [0] * len(AMINO_ACIDS21) * len(s)

            for i in range(len(s)):

                if s[i] in AMINO_ACIDS21:
                    index = AMINO_ACIDS21.index(s[i])

                else:
                    index = AMINO_ACIDS21['X']

                values[i*len(AMINO_ACIDS21) + index] = 1

            return Vectors.dense(values)

        session.udf.register("encoder", encoder, VectorUDT())

        self.data.createOrReplaceTempView("table")
        sql = f"SELECT *, encoder({self.inputCol}) AS {self.outputCol} from table"

        data = session.sql(sql)

        return data