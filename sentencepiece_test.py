################################################################################
# SentencePiece Test
################################################################################

import os, sys, traceback, argparse
import psutil, time
import glob
import sentencepiece as spm
import pandas as pd
import csv

################################################################################
# Functions
################################################################################

# 메모리 사용량 출력
def print_memory_usage(message):
    print(f'*** MEMORY USAGE: {psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2:.1f} MB ({message}) ***')

# 경과 시간 출력
def print_elapsed_time(start_time, end_time, message=''):
    elapsed_time = end_time - start_time
    message = f' ({message})' if len(message) > 0 else ''
    print(f'*** ELAPSED TIME: {elapsed_time:0.2f} seconds{message} ***')

# 파일 경로 출력
def print_output_filepath(filepath, message=''):
    message = f' ({message})' if len(message) > 0 else ''
    print(f'*** OUTPUT FILE{message}: {filepath}')

def scan_dir(dir):
    return glob.glob(os.path.join(dir, '**', '*.txt'))

def train_tokenizer(dir, alg, vocab_size):
    # How to decide: 8352, 24707?
    vocab_size = vocab_size if vocab_size is not None else 24707
    
    if not os.path.isdir(dir):
        raise Exception('Directory not found: ' + dir)
    
    #dir = os.path.abspath(dir)
    basename = os.path.basename(dir)
    
    # 훈련용 텍스트 파일 목록 만들기
    files = scan_dir(dir)
    data_file = ','.join(files)

    # 결과 디렉토리 만들기
    output_dir = f'./output/sentencepiece/{basename}_{alg}'
    os.makedirs(output_dir, exist_ok=True)

    # 모델 이름 지정
    model_prefix = os.path.join(output_dir, 'tokenizer')
    
    # 토크나이저 훈련
    start_time = time.time()

    spm.SentencePieceTrainer.Train(
        f'--input={data_file}' + 
        f' --model_prefix={model_prefix}' + 
        f' --vocab_size={vocab_size}' + 
        f' --model_type={alg}' + 
        f' --max_sentence_length={max_sentence_length}' + 
        f' --minloglevel=3'
    )

    print_elapsed_time(start_time, time.time())
    print_memory_usage('processing done')
    print_output_filepath(model_prefix)

    return model_prefix

def use_tokenizer(model_prefix):
    vocab_list = pd.read_csv(f'{model_prefix}.vocab', sep='\t', header=None, quoting=csv.QUOTE_NONE)
    print(f'훈련 결과 단어 목록 크기: {len(vocab_list)}')
    print(vocab_list.sample(10))

    # 토크나이저 사용
    sp = spm.SentencePieceProcessor()
    vocab_file = f'{model_prefix}.model'
    sp.load(vocab_file)

    lines = [
        '19.대종사 말씀하시기를 [스승이 법을 새로 내는 일이나, 제자들이 그 법을 받아서 후래 대중에게 전하는 일이나, 또 후래 대중이 그 법을 반가이 받들어 실행하는 일이 삼위 일체(三位一體)되는 일이라, 그 공덕도 또한 다름이 없나니라.]',
        '원불교는 대종사께서 창시하셨고 일원상 진리를 가르치신다.',
        '영광 길룡리 해변을 간척하다.',
        '천지는 대소유무의 이치를 따라 무심(無心)으로 운행할 뿐이기 때문이다.',
        '일원상의 수행은 삼학 팔조를 통해 삼대력을 얻어 무시선 무처선에 이르는 길',
        '개교표어'
    ]
    for line in lines:
        print('--------------------------------------------------------------------------------')
        print(f'{line}')
        #print()
        print(sp.encode_as_pieces(line))
        #print()
        #print(sp.encode_as_ids(line))
        #print()

    #print(sp.encode('개교표어', out_type=str))
    #print(sp.encode('개교표어', out_type=int))

################################################################################
# Variables
################################################################################

max_sentence_length = 9999

################################################################################
# Main
################################################################################

def main(args):
    dir = args.dir
    alg = args.alg
    vocab_size = args.vocab_size

    model_prefix = train_tokenizer(dir, alg, vocab_size)

    use_tokenizer(model_prefix)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(
            description="SentencePiece Test"
        )
        parser.add_argument(
            "--dir",
            type=str,
            required=True,
            help="Specifies a directory that has text files for training.",
        )
        parser.add_argument(
            "--alg",
            type=str,
            choices=['bpe', 'unigram'],
            required=True,
            help="Specifies the algorithm.",
        )
        parser.add_argument(
            "--vocab_size",
            type=int,
            required=False,
            help="Specifies the size of vocabulary.",
        )
        args = parser.parse_args()

        main(args)
    except:
        traceback.print_exc(file=sys.stdout)
        