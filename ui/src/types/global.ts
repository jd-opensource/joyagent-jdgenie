
declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace GenieType {
    type FCProps = {
      children?: React.ReactNode;
      /** 类名 */
      className?: string;
    }

    type FC<P extends object = object> = React.FC<P & FCProps>;

    type ControlProps<VAL = unknown, P = object> = {
      /** 需要自行加的值 */
      value?: VAL;
      /** 改变值时触发 */
      onChange?: (val: VAL) => void;
      /** 是否禁用 */
      disabled?: boolean;
    } & Omit<P, 'value' | 'onChange' | 'disabled'>;

    /**
     * 严格的omit，排除多个属性时使用此类型
     */
    type StrictOmit<T extends object, K extends keyof T> = Omit<T, K>;

    type OptionsType<T = string | number> = {
      label: React.ReactNode;
      value: T;
    };

    type Merge<T1, T2> = Omit<T1, keyof T2> & T2;
  }

  const SERVICE_BASE_URL: string;
}