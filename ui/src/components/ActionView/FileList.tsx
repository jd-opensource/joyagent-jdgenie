import { copyText, downloadFile, formatTimestamp, showMessage } from "@/utils";
import { keyBy } from "lodash";
import React, { useMemo, useState } from "react";
import ActionViewFrame from "./ActionViewFrame";
import classNames from "classnames";
import { FileRenderer, HTMLRenderer, PanelItemType, TableRenderer } from "../ActionPanel";
import { Empty, Tooltip } from "antd";
import { useBoolean, useMemoizedFn } from "ahooks";
import LoadingSpinner from "../LoadingSpinner";

type FileItem = {
  name: string;
  messageTime?: string;
  type: string;
  task: PanelItemType;
  url: string;
};

const messageTypeEnum = ['file', 'code', 'html', 'markdown', 'result', 'data_analysis'];

const FileList: GenieType.FC<{
  taskList?: PanelItemType[];
  activeFile?: CHAT.TFile;
  clearActiveFile?: () => void;
}> = (props) => {
  const { taskList, clearActiveFile, activeFile } = props;

  const [ activeItem, setActiveItem ] = useState<string | undefined>();
  const [ copying, { setFalse: stopCopying, setTrue: startCopying } ] = useBoolean(false);

  const clearActive = useMemoizedFn(() => {
    clearActiveFile?.();
    setActiveItem(undefined);
  });

  const {list: fileList, map: fileMap } = useMemo(() => {
    let map: Record<string, FileItem> = {};
    const list = (taskList || []).reduce<FileItem[]>((pre, task) => {
      const { resultMap } = task;
      if (messageTypeEnum.includes(task.messageType)) {
        const fileInfo: FileItem[] = (resultMap?.fileInfo ?? resultMap.fileList ?? []).map((item) => {
          const extension = item.fileName?.split('.')?.pop();
          return {
            ...item,
            name: item.fileName!,
            url: item.domainUrl!,
            task,
            messageTime: formatTimestamp(task.messageTime),
            type: extension!
          };
        });
        pre.push(...fileInfo.filter((item) => !map[item.name]));

        map = keyBy(pre, 'fileName');
      }
      return pre;
    }, []);
    return {
      list,
      map
    };
  }, [taskList]);
  // 当前选中的文件
  const fileItem = activeFile || (activeItem ? fileMap[activeItem] : undefined);
  const generateQuery = (name?: string, noHover?: boolean, click?: () => void) => {
    return <div className="flex-1 flex items-center w-0 h-full">
      <span
        className={classNames("cursor-pointer text-ellipsis whitespace-nowrap overflow-hidden", {'hover:font-medium': !noHover})}
        onClick={click || (() => setActiveItem(name))}
      >
        {name}
      </span>
    </div>;
  };

  let content: React.ReactNode = fileList.map((item) => (
    <div key={item.name} className="flex items-center pb-[16px]">
      <i className="font_family icon-rizhi mr-6"></i>
      {generateQuery(item.name)}
      <div className="text-[12px] text-[#8d8da5]">
        { item.messageTime}
      </div>
    </div>
  ));

  if (!fileList?.length) {
    content = <Empty />;
  }

  if (fileItem) {
    switch (fileItem.type) {
      case 'ppt':
      case 'html':
        content = <HTMLRenderer htmlUrl={fileItem.url} className="h-full" />;
        break;
      case 'csv':
      case 'xlsx':
        content = <TableRenderer fileUrl={fileItem.url} fileName={fileItem.name} />;
        break;
      default:
        content = <FileRenderer fileUrl={fileItem.url} fileName={fileItem.name} />;
        break;
    }
  }

  const copy = useMemoizedFn(async () => {
    if (!fileItem?.url) {
      return;
    }
    startCopying();
    const response = await fetch(fileItem.url);
    if (!response.ok) {
      stopCopying();
      throw new Error('Network response was not ok');
    }
    const data = await response.text();

    const copyData = data;

    // const parts = fileItem.name?.split('.');
    // const suffix = parts[parts.length - 1];
    // this.activeFileContent = data
    // const copyData = suffix === 'md' || suffix === 'txt' ? data : `\`\`\`${suffix}\n${data}\n\`\`\``;
    // this.markDownContent = this.md.render(
    //   suffix === 'md' || suffix === 'txt'
    //     ? data
    //     : `\`\`\`${suffix}\n${data}\n\`\`\``
    // )
    copyText(copyData);
    stopCopying();
    showMessage()?.success('复制成功');
  });

  return <ActionViewFrame
    className="p-16 overflow-y-auto"
    titleNode={fileItem && <>
      {generateQuery(fileItem?.name, true, clearActive)}
      <div className="flex items-center">
        <Tooltip title="下载">
          <i
            className="font_family rounded-[4px] size-20 flex items-center justify-center icon-xiazai mr-6 cursor-pointer hover:bg-gray-200"
            onClick={() => downloadFile(fileItem?.url.replace('preview', 'download'), fileItem.name)}
          ></i>
        </Tooltip>
        {/* excel文件不支持复制 */}
        {!['xlsx', 'xls'].includes(fileItem.type) && <Tooltip title="复制" placement="top">
          {copying ? <LoadingSpinner /> : <i className="font_family rounded-[4px] size-20 flex items-center justify-center icon-fuzhi cursor-pointer hover:bg-gray-200" onClick={copy}></i>}
        </Tooltip>}
      </div>
    </>}
    onClickTitle={() => clearActive()}
  >
    {content}
  </ActionViewFrame>;
};

export default FileList;

