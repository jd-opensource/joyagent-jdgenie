/**
 * 预览状态的tab选项
*/
import csvIcon from '@/assets/icon/CSV.png';
import docxIcon from '@/assets/icon/docx.png';
import excleIcon from '@/assets/icon/excle.png';
import pdfIcon from '@/assets/icon/pdf.png';
import txtIcon from '@/assets/icon/txt.png';
import htmlIcon  from '@/assets/icon/HTML.png';
import mov1 from '@/assets/mov/mov1.mp4';
import mov2 from '@/assets/mov/mov2.mp4';
import mov3 from '@/assets/mov/mov3.mp4';
import mov4 from '@/assets/mov/mov4.mp4';
import demo1 from '@/assets/icon/demo1.png';
import demo2 from '@/assets/icon/demo2.png';
import demo3 from '@/assets/icon/demo3.png';
import demo4 from '@/assets/icon/demo4.png';

import { ActionViewItemEnum } from "./enums";

export const iconType:Record<string, string> = {
  doc: docxIcon,
  docx: docxIcon,
  xlsx: excleIcon,
  csv: csvIcon,
  pdf: pdfIcon,
  txt: txtIcon,
  html: htmlIcon,
};

export const actionViewOptions = [
  {
    label: '实时跟随',
    value: ActionViewItemEnum.follow,
    split: false
  },
  {
    label: '浏览器',
    value: ActionViewItemEnum.browser,
  },
  {
    label: '文件',
    value: ActionViewItemEnum.file
  }
];

export const defaultActiveActionView = actionViewOptions[0].value;

export const productList = [{
  name: '网页模式',
  img: 'icon-diannao',
  type: 'html',
  placeholder: 'Genie会完成你的任务并以HTML网页方式输出报告',
  color: 'text-[#29CC29]'
},
{
  name: '文档模式',
  img: 'icon-wendang',
  type: 'docs',
  placeholder: 'Genie会完成你的任务并以markdown格式输出文档',
  color: 'text-[#4040FF]'
},
{
  name: 'PPT模式',
  img: 'icon-ppt',
  type: 'ppt',
  placeholder: 'Genie会完成你的任务并以PPT方式输出结论',
  color: 'text-[#FF860D]'
},
{
  name: '表格模式',
  img: 'icon-biaoge',
  type: 'table',
  placeholder: 'Genie会完成你的任务并以表格格式输出结论',
  color: 'text-[#FF3333]'
}];

export const defaultProduct = productList[0];

export const RESULT_TYPES = ['task_summary', 'result'];

export const InputSize:Record<string, string>  = {
  big: '106',
  medium: '72',
  small: '32'
};

export const demoList = [
  {
    title: 'Browser代码架构分析',
    description: '帮我分析github中开源的browser-use的代码，并进行分析',
    tag: '专业研究',
    videoUrl: mov1,
    url: '//storage.360buyimg.com/pubfree-bucket/ei-data-resource/89ab083/static/demoPage.html',
    image: demo1
  },
  {
    title: '京东财报分析',
    description: '分析一下京东的最新财务报告，总结出核心数据以及公司发展情况',
    tag: '数据分析',
    videoUrl: mov2,
    url: '//storage.360buyimg.com/pubfree-bucket/ei-data-resource/89ab083/static/demoPage2.html',
    image: demo2
  },
  {
    title: 'HR智能招聘产品竞品分析',
    description: '分析一下HR智能招聘领域的优秀产品，形成一个竞品对比报告',
    tag: '竞品调研',
    videoUrl: mov3,
    url: '//storage.360buyimg.com/pubfree-bucket/ei-data-resource/89ab083/static/demoPage3.html',
    image: demo3
  },
  {
    title: '超市销售数据分析',
    description: '帮我分析一下国内销售数据',
    tag: '数据分析',
    videoUrl: mov4,
    url: '//storage.360buyimg.com/pubfree-bucket/ei-data-resource/89ab083/static/demoPage4.html',
    image: demo4
  }
];
