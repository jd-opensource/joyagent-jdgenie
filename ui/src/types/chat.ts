declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace CHAT {
    export type ChatItem = GenieType.Merge<Pick<MESSAGE.Question, 'sessionId' | 'query' | 'requestId'>, {
      files: TFile[];
      plan?: MESSAGE.Plan;
      forceStop: boolean;
      tip?: string;
      multiAgent: MESSAGE.MultiAgent;
      agentType?: MESSAGE.ResultMap['agentType'];
      conclusion?: Task;
      responseType?: string;
      loading: boolean;
      tasks: Task[][],
      thought?: string;
      response?: string;
      taskStatus?: MESSAGE.MsgItem['taskStatus'];
      planList?: PlanItem[]
    }>

    type PlanItem = {
      name: string;
      list: string[];
    };

    export type TFile = {
      name: string,
      url: string,
      type: string,
      size: number
    }

    export type TInputInfo = {
      files?: TFile[];
      message: string;
      outputStyle?: string;
      deepThink: boolean;
    }

    export type TAbortController ={
      signal: AbortSignal;
      abort(reason?: any): void;
    }

    export type FetchEventSourceInit = {
      onopen: (event: Event) => void;
      onmessage: (event: any) => void;
      onerror: (event?: Event) => void;
      onclose: (event?: Event) => void;
      headers?: Record<string, string>;
      body?: string;
    }

    export type Task =GenieType.Merge<MESSAGE.Task, {
      resultMap: GenieType.Merge<MESSAGE.ResultMap, {
        searchResult?: GenieType.Merge<MESSAGE.SearchResult, {
          docs: MESSAGE.Doc[]
        }>,
        code?: string
      }>
      id: string;
      children?: Task[]
    }>

    export type FileList = MESSAGE.FileInfo

    type PlanStatus = MESSAGE.PlanStatus;

    export type Plan = MESSAGE.Plan;

    export type  Product = {
      name: string;
      img: string;
      type: string;
      placeholder: string;
      color: string;
  }
  }
}
