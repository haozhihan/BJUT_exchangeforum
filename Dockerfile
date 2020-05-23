FROM python:3.7.7
COPY . /debugger
WORKDIR /debugger
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
ENTRYPOINT ["python"]
CMD ["flasky.py"]