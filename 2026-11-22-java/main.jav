 1  package com.example.etl;
 2
 3  import java.io.BufferedReader;
 4  import java.io.IOException;
 5  import java.nio.charset.StandardCharsets;
 6  import java.nio.file.Files;
 7  import java.nio.file.Path;
 8  import java.util.ArrayList;
 9  import java.util.HashMap;
10  import java.util.List;
11  import java.util.Map;
12  import java.util.concurrent.ExecutorService;
13  import java.util.concurrent.Executors;
14
15  /**
16   * 일별 접속 로그 CSV 파일들을 병렬로 읽어 국가별 요청 수를 집계한다.
17   * 로그 형식(헤더 1줄 포함): timestamp,user_id,country_code,status
18   */
19  public class CountryRequestAggregator {
20
21      private final ExecutorService pool = Executors.newFixedThreadPool(8);
22      private final Map<String, Integer> countByCountry = new HashMap<>();
23      private int failedFiles = 0;
24
25      public Map<String, Integer> aggregate(List<Path> logFiles) {
26          for (Path file : logFiles) {
27              pool.submit(() -> processFile(file));
28          }
29          pool.shutdown();
30          return countByCountry;
31      }
32
33      private void processFile(Path file) {
34          try {
35              BufferedReader reader = Files.newBufferedReader(file, StandardCharsets.UTF_8);
36              String line;
37              reader.readLine(); // 헤더 건너뛰기
38              while ((line = reader.readLine()) != null) {
39                  String[] cols = line.split(",");
40                  String country = cols[2].trim().toUpperCase();
41                  if (country.isEmpty()) {
42                      continue;
43                  }
44                  countByCountry.merge(country, 1, Integer::sum);
45              }
46          } catch (IOException e) {
47              failedFiles++;
48              System.err.println("파일 읽기 실패: " + file);
49          }
50      }
51
52      public int getFailedFiles() {
53          return failedFiles;
54      }
55
56      public static void main(String[] args) throws IOException {
57          List<Path> files = new ArrayList<>();
58          try (var stream = Files.list(Path.of(args[0]))) {
59              stream.filter(p -> p.toString().endsWith(".csv"))
60                    .forEach(files::add);
61          }
62          CountryRequestAggregator agg = new CountryRequestAggregator();
63          Map<String, Integer> result = agg.aggregate(files);
64          result.entrySet().stream()
65                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
66                .limit(10)
67                .forEach(e -> System.out.println(e.getKey() + "\t" + e.getValue()));
68          System.out.println("실패 파일 수: " + agg.getFailedFiles());
69      }
70  }