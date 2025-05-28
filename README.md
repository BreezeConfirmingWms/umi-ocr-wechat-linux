# Umi-Ocr的wechat-linux插件







> 编译环境ubuntu 24.10   kernel 6.11.0-26-generic  libc6版本GNU C Library (Ubuntu GLIBC 2.40-1ubuntu3.1) stable release version 2.40. 需支持cpp20
>
> 确认`ls /proc/cpuinfo | grep AVX`支持飞桨OCR也即可以正常使用默认的Umi-ocr，使用umi-ocr/data自带的.embedded的python3.10环境，@[wcocr项目](https://github.com/swigger/wechat-ocr)自行进行`mkdir build &&cd build \ cmake .. && make -j$(nproc)`
>
> 感谢@[windows的wechatocr项目插件](https://github.com/eaeful/WechatOCR_umi_plugin/)的好想法，有空我会pull request
>
> ├── i18n.csv
> ├── __init__.py
> ├── wcocr.cpython-310-x86_64-linux-gnu.so(import wcocr必须依赖的)
> ├── WechatOCR_api.py(根据插件编写要求进行封装)
> └── WechatOCR_config.py

使用方法:

将本文件夹复制粘贴到<你的安装位置>/UmiOCR-data/plugins



实测速度310页18w字的技术书籍ocr时间为 :watch: ​5:14

![image-20250528220051877](/home/yum/.config/Typora/typora-user-images/image-20250528220051877.png)





以及若要使用覆盖源文档的功能 请定位到`<你的安装目录>/Umi-OCR_Linux/UmiOCR-data/py_src/ocr/output/output_pdf_layered.py` 将保存文件的名字修改为:

```python
#self.outputPath = f"{self.dir}/{self.fileName}.layered.pdf"
self.outputPath = f"{self.dir}/{self.fileName}.pdf"
```



![image-20250528220635546](/home/yum/.config/Typora/typora-user-images/image-20250528220635546.png)