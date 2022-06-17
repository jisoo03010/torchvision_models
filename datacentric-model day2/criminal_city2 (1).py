# -*- coding: utf-8 -*-
"""criminal_city2

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1am1pZL1Hk_wLjscBIye33e-qvKdc87An
"""

from google.colab import drive
drive.mount('/content/drive')

!unzip /content/drive/MyDrive/criminal_city/dataset2.zip -d /content/sample_data/

pip install |split-folders

import splitfolders

splitfolders.ratio('/content/sample_data/dataset2/', output="/content/sample_data/", seed=1337, ratio=(0.8, 0.2))

!nvidia-smi

import torchvision.models as models
import torch 
import splitfolders
from torch.utils.data import DataLoader 
from torch import nn 
import torchvision
from torchvision import transforms
import torchvision.datasets as datasets
import os





import numpy as np
import matplotlib.pyplot as plt

num_classes = 3
batch_size = 128
num_workers = 1 # 멀티 프로세싱과 관련된 파라미터
# lr = 0.002 
# 
lr = 0.00005

data_dir = '/content/sample_data/'
train_dir = os.path.join(data_dir, 'train')
test_dir = os.path.join(data_dir, 'valid')
print(train_dir)

data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),  # 이미지 사이즈 변경
        transforms.RandomHorizontalFlip(),  # 확률적으로 이미지를 수평으로 뒤집음
        # train 데이터를 랜덤으로 변형시켜서 학습 (overfitting 방지)
        transforms.ToTensor(), # numpy 이미지에서 torch (배열) 이미지로 변경
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'valid': transforms.Compose([
        transforms.Resize(256),             # 이미지 사이즈 변경 (전처리)
                                            # train으로 훈련시킨 모델의 정확도를 판별하기 위해 변형 X
        transforms.CenterCrop(224),         # 가운데를 224 사이즈로 자름
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
}

# 이미지 불러오기
datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),
                                    data_transforms[x])
                  for x in ['train', 'valid']}

dataloaders = {x: torch.utils.data.DataLoader(datasets[x], # train
                                              batch_size=batch_size, 
                                              # shuffle=False : 출력값의 숫자를 무작위 추출이 아닌 순차적 추출
                                              # shuflle=True : 출력값의 숫자를 순차적이 아닌 무작위로 값 출력
                                              shuffle=True,
                                              num_workers=num_workers, # cpu작업을 몇 개의 코어를 사용해서 진행할지에 대한 설정 
                                              pin_memory=True,
                                              drop_last=False)
               for x in ['train', 'valid']}

print(len(datasets['valid'])+ len(datasets['train']))
datasets['train'].classes

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")



def imshow(input, title):
    # torch.Tensor를 numpy 객체로 변환
    input = input.numpy().transpose((1, 2, 0))
    # 이미지 정규화 해제하기
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    input = std * input + mean
    input = np.clip(input, 0, 1)
    # 이미지 출력
    plt.imshow(input)
    plt.title(title)
    plt.show()
iterator = iter(dataloaders['train'])
inputs, classes = next(iterator)
out = torchvision.utils.make_grid(inputs)
imshow(out, title=classes)

classes

model =  models.convnext_tiny(pretrained=False, quantize=True, num_classes=num_classes)
model

model.to(device)



"""##  **모델 학습시키기**

"""

# for x, y in enumerate(dataloaders):
#         print('x : ', x.to(device))
#         print('y : ', y.to(device))

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=lr)

train_loss = [0]
test_loss = [0]

epochs = 16
for t in range(epochs):
  def train(dataloaders, model, loss_fn, optimizer):
    size = len(datasets['valid'])+ len(datasets['train'])
    for batch, (x, y) in enumerate(dataloaders):
      x, y = x.to(device), y.to(device)
      correct = 0
      total = 0
      pred = model(x) # 모델 입력한 값
      loss = loss_fn(pred, y)
      total += len(classes)



      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
      train_loss.append(loss)
      if batch % 100 == 0:
        loss, current = loss.item(), batch * len(x)
        print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}] total : {total}")

  def valid(dataloaders, model, loss_fn):
    size = len(datasets['valid'])+ len(datasets['train'])
    num_batches = len(dataloaders)
    model.eval()
    test_loss1, correct = 0, 0
    with torch.no_grad():
      for x, y in dataloaders:
        total = 0
        correct = 0
        x, y = x.to(device), y.to(device)
        pred = model(x)
        total += len(y)
        test_loss1 = loss_fn(pred, y)
        correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    
    test_loss.append(test_loss1)
    print(f"Test Error: \n Accuracy: {100 * ( correct / total):>0.1f}%, Avg loss: {test_loss1:>8f} \n")



  print(f"Epoch {t+1}\n-------------------------------")
  train(dataloaders['train'], model, loss_fn, optimizer)
  valid(dataloaders['valid'], model, loss_fn)
  print("Done!")

test_loss

import matplotlib.pyplot as plt 
plt.plot(torch.Tensor(train_loss), label='train loss')
plt.plot(torch.Tensor(test_loss), label='valid loss')
plt.legend()









# convnext_small = models.convnext_small()
# convnext_base = models.convnext_base()
# convnext_large = models.convnext_large()
# convnext_tiny = models.convnext_tiny()
# convnext_tiny

