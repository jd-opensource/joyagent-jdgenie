package com.jd.genie.model.multi;

import com.alibaba.fastjson.JSONObject;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EventResult {
    /**
     * 增量消息计数
     */
    private AtomicInteger messageCount = new AtomicInteger(0);

    /**
     * 增量消息偏移量（从 1 开始）
     */
    private Map<String, Integer> orderMapping = new HashMap<>();

    public Integer getAndIncrOrder(String key) {
        Integer order = orderMapping.get(key);
        if (Objects.isNull(order)) {
            orderMapping.put(key, 1);
            return 1;
        }
        orderMapping.put(key, order + 1);
        return order + 1;
    }

    /**
     * 增量计划-初始化标识
     */
    public Boolean initPlan;

    public Boolean isInitPlan() {
        if (Objects.isNull(initPlan) || Boolean.FALSE.equals(initPlan)) {
            this.initPlan = true;
            return true;
        }
        return false;
    }

    /**
     * 增量任务
     */
    private String taskId;
    private AtomicInteger taskOrder = new AtomicInteger(1);

    public String getTaskId() {
        if (Objects.isNull(this.taskId) || this.taskId.isEmpty()) {
            this.taskId = UUID.randomUUID().toString();
        }
        return this.taskId;
    }

    public String renewTaskId() {
        this.getTaskOrder().set(1);
        this.taskId = UUID.randomUUID().toString();
        return this.taskId;
    }

    /**
     * 增量任务-流式消息类型
     */
    private List<String> streamTaskMessageType = new ArrayList<String>() {{
        add("html");
        add("markdown");
        add("deep_search");
        add("multimodalagent_tool");
        add("tool_thought");
        add("data_analysis");
    }};

    /**
     * 全量结果（回放）
     */
    private Map<String, Object> resultMap = new HashMap<>();

    public List<Object> getResulMapTask() {
        if (this.resultMap.containsKey("tasks")) {
            Object obj = this.resultMap.get("tasks");
            return (List<Object>) obj;
        }
        return null;
    }

    public void setResultMapTask(List<Object> task) {
        List<Object> tasks = this.getResulMapTask();
        if (Objects.isNull(tasks)) {
            tasks = new ArrayList<Object>() {{
                add(task);
            }};
            this.resultMap.put("tasks", tasks);
            return;
        }
        tasks.add(task);
    }

    public void setResultMapSubTask(Object subTask) {
        List<Object> tasks = this.getResulMapTask();
        if (Objects.isNull(tasks)) {
            tasks = new ArrayList<Object>() {{
                add(new ArrayList<>());
            }};
            this.resultMap.put("tasks", tasks);
        }
        List<Object> subTasks = (List<Object>) tasks.get(tasks.size() - 1);
        subTasks.add(subTask);
    }

    /**
     * 全量结果（重连）
     */
    private List<Object> resultList = new ArrayList<>();

    public static void main(String[] args) {
        EventResult res = new EventResult();
        List<Object> task = new ArrayList<>();
        res.setResultMapTask(task);
        List<Object> subTask = new ArrayList<Object>();
        res.setResultMapSubTask(subTask);
        List<Object> task1 = new ArrayList<Object>() {{
            add("task1");
        }};
        res.setResultMapTask(task1);
        List<Object> task2 = new ArrayList<Object>() {{
            add("task2");
        }};
        res.setResultMapTask(task2);
        List<Object> subTask2 = new ArrayList<Object>();
        res.setResultMapSubTask(subTask2);
        System.out.println(JSONObject.toJSONString(res.getResultMap()));
    }
}
