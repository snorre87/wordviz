import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ['sentida==0.6.0','danlp==0.1.0','allennlp==2.7.0','hisia==0.3.1','afinn==0.1',
'urllib3==1.26.7'] # google-cloud-storage

# installing packages
inp = input('Will install needed packages (only recommended on rebootable server / sandbox). Do you want to install? y or Enter.')

if inp =='y':
    print('Installing packages: %s'%('-'.join(packages)))
    import tqdm
    for package in tqdm.tqdm(packages):
        install(package)
    print('Done installing packages')
import nltk,numpy as np
nltk.download('punkt')
import operator
import time
class DANISH_SENTIMENT():
  def __init__(self,hisia=True):
    try:
      from afinn import Afinn
      self.afinn = Afinn(language='da')
    except:
      print('afinn not installed')
      self.afinn = False
    try:
      from sentida import Sentida
      self.sent = Sentida()
    except:
      print('sentida not loading')
      self.sent = False
    try:
      from danlp.models import load_bert_emotion_model
      self.classifier = load_bert_emotion_model()
    except:
      self.classifier = False
      print('bert emotion not loading')

    try:
      from danlp.models import load_bert_tone_model
      self.classifier_tone = load_bert_tone_model()
    except:
      print('bert tone not working')
      self.classifier_tone = False
    try:
      from danlp.models import load_spacy_model
      self.nlp = load_spacy_model(textcat='sentiment',vectorError=True) # if you got an error saying da.vectors not found, try setting vectorError=True - it is an temp fix
    except:
      print('spacy sentiment not working')
      self.nlp = False
    if hisia:
      try:
        from hisia import Hisia
        self.hisia = Hisia
      except:
        self.hisia = False
        print('hisia not working')
    else:
      self.hisia=False
  def get_bert(self,text,clf,kwargs={}):
    res = clf.predict_proba(text, **kwargs)
    d_s = {}
    classes = clf._classes()
    d = {}
    for num in range(len(classes)):
        em = res[num]
        cl = classes[num]
        best = em.argmax()
        d_s[num] = cl[best]
        for i,j in zip(cl,em):
          d[i] = j
    return d,d_s
  def get_sentiment(self,text,timings=False):
    d = {}
    if text.strip()=='':
        return d
    funcs = [lambda x: self.afinn.score(x),
    lambda text:self.sent.sentida(text,output='total',normal=True,speed ='normal'),
    lambda x: self.get_bert(x,clf=self.classifier,kwargs={'no_emotion':True}),
    lambda text: self.get_bert(text,clf=self.classifier_tone),
        lambda text: self.hisia(text).sentiment.positive_probability,
        lambda text: self.nlp(text).cats]
    names = ['afinn','sentida','bert_emotion','bert_tone','hisia_posprob','spacy_sent']
    d_t = {}
    d_s = {}
    for func,name in zip(funcs,names):
        try:
            t = time.time()
            out = func(text)
            if type(out)!=tuple:
                d[name] = out
                if type(out)==dict:
                    d_s[name] = max(out,key=lambda x:x[1])
                else:
                    d_s[name] = out
            else:
                d[name] = out[0]
                d_s[name] = out[1]

            dt = time.time()-t
            d_t[name] = dt
        except Exception as e:
            pass
    d,d_s = recursive_float(d),recursive_float(d_s)
    if timings:
      return d,d_s,d_t
    return d,d_s
def tofloat(val):
  try:
    return float(val)
  except:
    return val
def recursive_float(d):
  if not type(d)==dict:
    return d
  new_d = {}
  for key in d:
    val = d[key]
    if hasattr(val, '__iter__'):
      # recursive application
      val = recursive_float(val)
    val = tofloat(val)
    new_d[key] = val
  return new_d
