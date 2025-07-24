import React, { useMemo, useRef, useState } from "react";
import { Input, Button, Tooltip } from "antd";
import classNames from "classnames";
import { TextAreaRef } from "antd/es/input/TextArea";
import { getOS } from "@/utils";

const { TextArea } = Input;

type Props = {
  placeholder: string;
  showBtn: boolean;
  disabled: boolean;
  size: string;
  product?: CHAT.Product;
  send: (p: CHAT.TInputInfo) => void;
};

const GeneralInput: GenieType.FC<Props> = (props) => {
  const { placeholder, showBtn, disabled, product, send } = props;
  const [question, setQuestion] = useState<string>("");
  const [deepThink, setDeepThink] = useState<boolean>(false);
  const textareaRef = useRef<TextAreaRef>(null);
  const tempData = useRef<{
    cmdPress?: boolean;
    compositing?: boolean;
  }>({});

  const questionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuestion(e.target.value);
  };

  const changeThinkStatus = () => {
    setDeepThink(!deepThink);
  };

  const pressEnter: React.KeyboardEventHandler<HTMLTextAreaElement> = () => {
    if (tempData.current.compositing) {
      return;
    }
    // 按住command 回车换行逻辑
    if (tempData.current.cmdPress) {
      const textareaDom = textareaRef.current?.resizableTextArea?.textArea;
      if (!textareaDom) {
        return;
      }
      const { selectionStart, selectionEnd } = textareaDom || {};
      const newValue =
        question.substring(0, selectionStart) +
        '\n' + // 插入换行符
        question.substring(selectionEnd!);

      setQuestion(newValue);
      setTimeout(() => {
        textareaDom.selectionStart = selectionStart! + 1;
        textareaDom.selectionEnd = selectionStart! + 1;
        textareaDom.focus();
      }, 20);
      return;
    }
    // 屏蔽状态，不发
    if (!question || disabled) {
      return;
    }
    send({
      message: question,
      outputStyle: product?.type,
      deepThink,
    });
    setQuestion("");
  };

  const sendMessage = () => {
    send({
      message: question,
      outputStyle: product?.type,
      deepThink,
    });
    setQuestion("");
  };

  const enterTip = useMemo(() => {
    return `⏎发送，${getOS() === 'Mac' ? '⌘' : '^'} + ⏎ 换行`;
  }, []);

  return (
    <div
      className={
        showBtn
          ? "rounded-[12px] bg-[linear-gradient(to_bottom_right,#4040ff,#ff49fd,#d763fc,#3cc4fa)] p-1"
          : ""
      }
    >
      <div className="rounded-[12px] border border-[#E9E9F0] overflow-hidden p-[12px] bg-[#fff]">
        <div className="relative">
          <TextArea
            ref={textareaRef}
            value={question}
            placeholder={placeholder}
            className={classNames(
              "h-62 no-border-textarea border-0 resize-none p-[0px] focus:border-0 bg-[#fff]",
              showBtn && product ? "indent-86" : ""
            )}
            onChange={questionChange}
            onPressEnter={pressEnter}
            onKeyDown={(event) => {
              tempData.current.cmdPress = event.metaKey || event.ctrlKey;
            }}
            onKeyUp={() => {
              tempData.current.cmdPress = false;
            }}
            onCompositionStart={() => {
              tempData.current.compositing = true;
            }}
            onCompositionEnd={() => {
              tempData.current.compositing = false;
            }}
          />
          {showBtn && product ? (
            <div className="h-[24px] w-[80px] absolute top-0 left-0 flex items-center justify-center rounded-[6px] bg-[#f4f4f9] text-[12px] ">
              <i className={`font_family ${product.img} ${product.color} text-14`}></i>
              <div className="ml-[6px]">{product.name}</div>
            </div>
          ) : null}
        </div>
        <div className="h-30 flex justify-between items-center mt-[6px]">
          {showBtn ? (
            <Button
              color={deepThink ? "primary" : "default"}
              variant="outlined"
              className={classNames(
                "text-[12px] p-[8px] h-[28px] transition-all hover:text-[#333] hover:bg-[rgba(64,64,255,0.02)] hover:border-[rgba(64,64,255,0.2)]",
              )}
              onClick={changeThinkStatus}
            >
              <i className="font_family icon-shendusikao"></i>
              <span className="ml-[-4px]">深度研究</span>
            </Button>
          ) : (
            <div></div>
          )}
          <div className="flex items-center">
            <span className="text-[12px] text-gray-300 mr-8 flex items-center">
              {enterTip}
            </span>
            <Tooltip title="发送">
              <i
                className={`font_family icon-fasongtianchong ${!question || disabled ? "cursor-not-allowed text-[#ccc] pointer-events-none" : "cursor-pointer"}`}
                onClick={sendMessage}
              ></i>
            </Tooltip>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeneralInput;
