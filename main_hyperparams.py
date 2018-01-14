#! /usr/bin/env python
import os
import argparse
import datetime
import torch
import torchtext.data as data
from Dataloader import mydatasets_self_two
from Dataloader.Load_Pretrained_Embedding import Word_Embedding
import train_ALL_CNN
from models import model_CNN
import multiprocessing as mu
import shutil
import random
import hyperparams
# solve encoding
# @Author : bamtercelboo
# @Datetime : 2018/1/14 22:45
# @File : hyperparams.py
# @Last Modify Time : 2018/1/14 22:45
# @Contact : bamtercelboo@{gmail.com, 163.com}

"""
    File : main_hyperparams.py
    Function : main function
"""
from imp import reload
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

# random seed
torch.manual_seed(hyperparams.seed_num)
random.seed(hyperparams.seed_num)

parser = argparse.ArgumentParser(description="text classification")
# learning
parser.add_argument('-lr', type=float, default=hyperparams.learning_rate, help='initial learning rate [default: 0.001]')
parser.add_argument('-epochs', type=int, default=hyperparams.epochs, help='number of epochs for train [default: 256]')
parser.add_argument('-batch-size', type=int, default=hyperparams.batch_size, help='batch size for training [default: 64]')
parser.add_argument('-log-interval',  type=int, default=hyperparams.log_interval,   help='how many steps to wait before logging training status [default: 1]')
parser.add_argument('-test-interval', type=int, default=hyperparams.test_interval, help='how many steps to wait before testing [default: 100]')
parser.add_argument('-save-interval', type=int, default=hyperparams.save_interval, help='how many steps to wait before saving [default:500]')
parser.add_argument('-save-dir', type=str, default=hyperparams.save_dir, help='where to save the snapshot')
# Data
parser.add_argument('-datafile_path', type=str, default=hyperparams.datafile_path, help='datafile path')
parser.add_argument('-name_trainfile', type=str, default=hyperparams.name_trainfile, help='train file name')
parser.add_argument('-name_devfile', type=str, default=hyperparams.name_devfile, help='dev file name')
parser.add_argument('-name_testfile', type=str, default=hyperparams.name_testfile, help='test file name')
parser.add_argument('-shuffle', action='store_true', default=hyperparams.shuffle, help='shuffle the Data every epoch' )
parser.add_argument('-epochs_shuffle', action='store_true', default=hyperparams.epochs_shuffle, help='shuffle the Data every epoch' )
# task select
parser.add_argument('-TWO_CLASS_TASK', action='store_true', default=hyperparams.TWO_CLASS_TASK, help='whether to execute two-classification-task')
# optim select
parser.add_argument('-Adam', action='store_true', default=hyperparams.Adam, help='whether to select Adam to train')
parser.add_argument('-SGD', action='store_true', default=hyperparams.SGD, help='whether to select SGD to train')
parser.add_argument('-Adadelta', action='store_true', default=hyperparams.Adadelta, help='whether to select Adadelta to train')
# model
parser.add_argument('-char_data', action='store_true', default=hyperparams.char_data, help='whether to use ')
parser.add_argument('-rm_model', action='store_true', default=hyperparams.rm_model, help='whether to delete the model after test acc so that to save space')
parser.add_argument('-init_weight', action='store_true', default=hyperparams.init_weight, help='init w')
parser.add_argument('-init_weight_value', type=float, default=hyperparams.init_weight_value, help='value of init w')
parser.add_argument('-init_weight_decay', type=float, default=hyperparams.weight_decay, help='value of init L2 weight_decay')
parser.add_argument('-momentum_value', type=float, default=hyperparams.optim_momentum_value, help='value of momentum in SGD')
parser.add_argument('-init_clip_max_norm', type=float, default=hyperparams.clip_max_norm, help='value of init clip_max_norm')
parser.add_argument('-seed_num', type=float, default=hyperparams.seed_num, help='value of init seed number')
parser.add_argument('-dropout', type=float, default=hyperparams.dropout, help='the probability for dropout [default: 0.5]')
parser.add_argument('-dropout_embed', type=float, default=hyperparams.dropout_embed, help='the probability for dropout [default: 0.5]')
parser.add_argument('-max-norm', type=float, default=hyperparams.max_norm, help='l2 constraint of parameters [default: 3.0]')
parser.add_argument('-embed-dim', type=int, default=hyperparams.embed_dim, help='number of embedding dimension [default: 128]')
parser.add_argument('-kernel-num', type=int, default=hyperparams.kernel_num, help='number of each kind of kernel')
parser.add_argument('-kernel-sizes', type=str, default=hyperparams.kernel_sizes, help='comma-separated kernel size to use for convolution')
parser.add_argument('-static', action='store_true', default=hyperparams.static, help='fix the embedding')
parser.add_argument('-CNN', action='store_true', default=hyperparams.CNN, help='whether to use CNN model')
parser.add_argument('-BiLSTM_1', action='store_true', default=hyperparams.BiLSTM_1, help='whether to use BiLSTM_1 model')
parser.add_argument('-wide_conv', action='store_true', default=hyperparams.wide_conv, help='whether to use wide conv')
parser.add_argument('-word_Embedding', action='store_true', default=hyperparams.word_Embedding, help='whether to load word embedding')
parser.add_argument('-word_Embedding_Path', type=str, default=hyperparams.word_Embedding_Path, help='filename of model snapshot [default: None]')
parser.add_argument('-lstm-hidden-dim', type=int, default=hyperparams.lstm_hidden_dim, help='the number of embedding dimension in LSTM hidden layer')
parser.add_argument('-lstm-num-layers', type=int, default=hyperparams.lstm_num_layers, help='the number of embedding dimension in LSTM hidden layer')
parser.add_argument('-min_freq', type=int, default=hyperparams.min_freq, help='min freq to include during built the vocab')
# nums of threads
parser.add_argument('-num_threads', type=int, default=hyperparams.num_threads, help='the num of threads')
# device
parser.add_argument('-device', type=int, default=hyperparams.device, help='device to use for iterate Data, -1 mean cpu [default: -1]')
parser.add_argument('-no_cuda', action='store_true', default=hyperparams.no_cuda, help='disable the gpu')
# option
args = parser.parse_args()


# load two-classification Data
def mrs_two(path, train_name, dev_name, test_name, char_data, text_field, label_field, **kargs):
    train_data, dev_data, test_data = mydatasets_self_two.MR.splits(path, train_name, dev_name, test_name,
                                                                    char_data, text_field, label_field)
    print("len(train_data) {} ".format(len(train_data)))
    text_field.build_vocab(train_data.text, min_freq=args.min_freq)
    label_field.build_vocab(train_data.label)
    train_iter, dev_iter, test_iter = data.Iterator.splits(
                                        (train_data, dev_data, test_data),
                                        batch_sizes=(args.batch_size, len(dev_data), len(test_data)),
                                        **kargs)
    return train_iter, dev_iter, test_iter

# load Data
text_field = data.Field(lower=True)
label_field = data.Field(sequential=False)
print("\nLoading Data...")
if args.TWO_CLASS_TASK:
    print("Executing 2 Classification Task......")
    train_iter, dev_iter, test_iter = mrs_two(args.datafile_path, args.name_trainfile,
                                              args.name_devfile, args.name_testfile, args.char_data, text_field,
                                              label_field, device=-1, repeat=False, shuffle=args.epochs_shuffle)

    '''
    # handle external word embedding to file for convenience
    from Dataloader.handle_wordEmbedding2File import WordEmbedding2File
    wordembedding = WordEmbedding2File(wordEmbedding_path="./word2vec/glove.sentiment.conj.pretrained.txt",
                                       vocab=text_field.vocab.itos, k_dim=300)
    wordembedding.handle()
    '''
# load word2vec
if args.word_Embedding:
    word_embedding = Word_Embedding()
    if args.embed_dim is not None:
        print("word_Embedding_Path {} ".format(args.word_Embedding_Path))
        path = args.word_Embedding_Path
    print("loading word2vec vectors...")
    word_vecs = word_embedding.load_my_vecs(path, text_field.vocab.itos, text_field.vocab.freqs, k=args.embed_dim)
    print("word2vec loaded!")
    print("num words already in word2vec: " + str(len(word_vecs)))
    print("loading unknown word2vec and convert to list...")
    print("loading unknown word by avg......")
    # word_vecs = add_unknown_words_by_uniform(word_vecs, text_field.vocab.itos, k=args.embed_dim)
    word_vecs = word_embedding.add_unknown_words_by_avg(word_vecs, text_field.vocab.itos, k=args.embed_dim)
    print("len(word_vecs) {} ".format(len(word_vecs)))
    print("unknown word2vec loaded ! and converted to list...")



# update args and print
args.embed_num = len(text_field.vocab)
args.class_num = len(label_field.vocab) - 1
args.cuda = (args.no_cuda) and torch.cuda.is_available(); del args.no_cuda
args.kernel_sizes = [int(k) for k in args.kernel_sizes.split(',')]
# save file
mulu = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
args.mulu = mulu
args.save_dir = os.path.join(args.save_dir, mulu)
if not os.path.isdir(args.save_dir):
    os.makedirs(args.save_dir)

# load word2vec
if args.word_Embedding:
    args.pretrained_weight = word_vecs

# print parameters
print("\nParameters:")
if os.path.exists("./Parameters.txt"):
    os.remove("./Parameters.txt")
file = open("Parameters.txt", "a")
for attr, value in sorted(args.__dict__.items()):
    if attr.upper() != "PRETRAINED_WEIGHT" and attr.upper() != "pretrained_weight_static".upper():
        print("\t{}={}".format(attr.upper(), value))
    file.write("\t{}={}\n".format(attr.upper(), value))
file.close()
shutil.copy("./Parameters.txt", "./snapshot/" + mulu + "/Parameters.txt")
shutil.copy("./hyperparams.py", "./snapshot/" + mulu)

# model
if args.CNN is True:
    print("loading CNN model.....")
    model = model_CNN.CNN_Text(args)
    # save model in this time
    shutil.copy("./models/model_CNN.py", "./snapshot/" + mulu)

if args.cuda is True:
    print("using cuda......")
    model = model.cuda()
print(model)
        

# train
print("\n cpu_count \n", mu.cpu_count())
torch.set_num_threads(args.num_threads)
if os.path.exists("./Test_Result.txt"):
    os.remove("./Test_Result.txt")
if args.CNN is True:
    print("CNN training start......")
    model_count = train_ALL_CNN.train(train_iter, dev_iter, test_iter, model, args)
print("Model_count", model_count)

resultlist = []
if os.path.exists("./Test_Result.txt"):
    file = open("./Test_Result.txt")
    for line in file.readlines():
        if line[:10] == "Evaluation":
            resultlist.append(float(line[34:41]))
    result = sorted(resultlist)
    file.close()
    file = open("./Test_Result.txt", "a")
    file.write("\nThe Best Result is : " + str(result[len(result) - 1]))
    file.write("\n")
    file.close()
    shutil.copy("./Test_Result.txt", "./snapshot/" + mulu + "/Test_Result.txt")
