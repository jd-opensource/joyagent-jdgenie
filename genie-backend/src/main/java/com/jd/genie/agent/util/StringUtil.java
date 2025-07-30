package com.jd.genie.agent.util;

import java.security.SecureRandom;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class StringUtil {
    private static final String CHAR_LOWER = "abcdefghijklmnopqrstuvwxyz";
    private static final String NUMBER = "0123456789";
    private static final String DATA_FOR_RANDOM_STRING = CHAR_LOWER + NUMBER;
    private static final SecureRandom random = new SecureRandom();

    public static String generateRandomString(int length) {
        if (length < 1) throw new IllegalArgumentException();

        StringBuilder sb = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            // 生成 0 到 DATA_FOR_RANDOM_STRING 长度之间的随机索引
            int rndCharAt = random.nextInt(DATA_FOR_RANDOM_STRING.length());
            char rndChar = DATA_FOR_RANDOM_STRING.charAt(rndCharAt);
            sb.append(rndChar);
        }
        return sb.toString();
    }

    // 银行卡Luhn校验算法
    private static boolean luhnBankCardVerify(String cardNumber) {
        int sum = 0;
        boolean alternate = false;
        for (int i = cardNumber.length() - 1; i >= 0; i--) {
            int digit = Character.getNumericValue(cardNumber.charAt(i));
            if (alternate) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }
            sum += digit;
            alternate = !alternate;
        }
        return (sum % 10 == 0);
    }

    public static String textDesensitization(String content, Map<String, String> sensitivePatternsMapping) {
        // 邮箱地址脱敏
        Pattern emailPattern = Pattern.compile("[a-zA-Z0-9\\._%\\+\\-]+@[a-zA-Z0-9\\.-]+\\.[a-zA-Z]{2,}");
        Matcher emailMatcher = emailPattern.matcher(content);
        while (emailMatcher.find()) {
            String snippet = emailMatcher.group();
            int maskIdx = snippet.indexOf("@");
            // 内部邮箱不处理
            if (content.contains("@jd.com")) {
                continue;
            }
            content = content.replace(snippet, snippet.substring(0, maskIdx) + "＠" + snippet.substring(maskIdx + 1));
        }

        // 身份证号脱敏
        Pattern idPattern = Pattern.compile("(?:[^\\dA-Za-z_]|^)((?:[1-6][1-7]|50|71|81|82)\\d{4}(?:19|20)\\d{2}(?:0[1-9]|10|11|12)(?:[0-2][1-9]|10|20|30|31)\\d{3}[0-9Xx])(?:[^\\dA-Za-z_]|$)");
        Matcher idMatcher = idPattern.matcher(content);
        while (idMatcher.find()) {
            String snippet = idMatcher.group(1);
            content = content.replace(snippet, snippet.substring(0, 12) + "✿✿✿✿✿✿");
        }

        // 手机号脱敏
        Pattern phonePattern = Pattern.compile("(?:[^\\dA-Za-z_]|^)(1[3456789]\\d{9})(?:[^\\dA-Za-z_]|$)");
        Matcher phoneMatcher = phonePattern.matcher(content);
        while (phoneMatcher.find()) {
            String snippet = phoneMatcher.group(1);
            content = content.replace(snippet, snippet.substring(0, 3) + "✿✿✿✿" + snippet.substring(7));
        }

        // 银行卡号脱敏
        Pattern bankcardPattern = Pattern.compile("(?:[^\\dA-Za-z_]|^)(62(?:\\d{14}|\\d{17}))(?:[^\\dA-Za-z_]|$)");
        Matcher bankcardMatcher = bankcardPattern.matcher(content);
        while (bankcardMatcher.find()) {
            String snippet = bankcardMatcher.group(1);
            if (luhnBankCardVerify(snippet)) {
                content = content.replace(snippet, snippet.substring(0, 12) + "✿✿✿✿✿✿");
            }
        }

        // 密码及其他敏感词脱敏
        for (Map.Entry<String, String> entry : sensitivePatternsMapping.entrySet()) {
            String pattern = entry.getKey();
            String wordMapping = entry.getValue();

            int startIndex = pattern.indexOf("^)") + 2;
            int endIndex = pattern.lastIndexOf("[^");

            if (startIndex + 1 < endIndex) {
                String sensitiveWord = pattern.substring(startIndex, endIndex);
                Pattern sensitivePattern = Pattern.compile(pattern);
                Matcher sensitiveMatcher = sensitivePattern.matcher(content);

                while (sensitiveMatcher.find()) {
                    String snippet = sensitiveMatcher.group();
                    if (content.startsWith(sensitiveWord)) {
                        content = content.replace(snippet, wordMapping + snippet.substring(snippet.length() - 1));
                    } else {
                        content = content.replace(snippet, snippet.charAt(0) + wordMapping + snippet.substring(snippet.length() - 1));
                    }
                }
            } else {
                content = content.replace(pattern, wordMapping);
            }
        }

        return content;
    }

    public static String removeSpecialChars(String input) {
        if (Objects.isNull(input) || input.isEmpty()) {
            return "";
        }
        // 定义需要过滤的特殊字符集合
        String specialChars = " \"&$@=;+?\\{^}%~[]<>#|'";
        Set<Character> specialCharsSet = new HashSet<>();
        for (char c : specialChars.toCharArray()) {
            specialCharsSet.add(c);
        }
        StringBuilder result = new StringBuilder();
        for (char c : input.toCharArray()) {
            if (!specialCharsSet.contains(c)) {
                result.append(c);
            }
        }
        return result.toString();
    }

    public static String getUUID() {
        UUID uuid = UUID.randomUUID();
        return uuid.toString();
    }

    public static boolean isEmpty(String str){
        return str == null || str.trim().isEmpty();
    }
    
    public static boolean isNotEmpty(String str){
        return !isEmpty(str);
    }

    public static void main(String[] args) {

        System.out.println(getUUID());

        /*String name = "123 $ 456 %%% ^ ";
        System.out.println(removeSpecialChars(name));

        name = null;
        System.out.println(">>" + removeSpecialChars(name) + "<<");

        Map<String, String> patterns = new HashMap<>();
        patterns.put("(?:[^A-Za-z0-9_-]|^)password[^A-Za-z0-9_-]", "PASSWORD");
        patterns.put("(?:[^A-Za-z0-9_-]|^)asd[^A-Za-z0-9_-]", "ASD");

        String testContent = "asd 我的邮箱是test@example.com，身份证号是510104199001011234，手机号是13800138000，银行卡号是6226327514303272，哈哈password:::admin123 asd";
        String result = textDesensitization(testContent, patterns);
        System.out.println(result);*/
    }
}
