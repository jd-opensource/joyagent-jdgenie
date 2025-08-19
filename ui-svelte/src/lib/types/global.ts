export type FCProps = {
  children?: any;
  className?: string;
}

export type ControlProps<VAL = unknown, P = object> = {
  value?: VAL;
  onChange?: (val: VAL) => void;
  disabled?: boolean;
} & Omit<P, 'value' | 'onChange' | 'disabled'>;

export type StrictOmit<T extends object, K extends keyof T> = Omit<T, K>;

export type OptionsType<T = string | number> = {
  label: string;
  value: T;
};

export type Merge<T1, T2> = Omit<T1, keyof T2> & T2;

declare global {
  const SERVICE_BASE_URL: string;
}