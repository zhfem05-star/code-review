package org.apache.kafka.common.utils.internals;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

// 실행용 드라이버 (리뷰 대상 아님)
// input.txt 한 줄 = initialInterval multiplier maxInterval jitter maxAttempts samples
// '#'으로 시작하는 줄과 빈 줄은 건너뜀
public class BackoffDemo {
    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.err.println("usage: java -cp out org.apache.kafka.common.utils.internals.BackoffDemo <input.txt>");
            System.exit(1);
        }
        List<String> lines = Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8);
        for (String raw : lines) {
            String line = raw.strip();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            String[] p = line.split("\\s+");
            if (p.length < 6) {
                System.out.println("[skip] 값이 6개 필요: " + line);
                continue;
            }
            System.out.println("=== " + line);
            try {
                long initial = Long.parseLong(p[0]);
                int multiplier = Integer.parseInt(p[1]);
                long max = Long.parseLong(p[2]);
                double jitter = Double.parseDouble(p[3]);
                int maxAttempts = Integer.parseInt(p[4]);
                int samples = Integer.parseInt(p[5]);

                ExponentialBackoff backoff = new ExponentialBackoff(initial, multiplier, max, jitter);
                System.out.println(backoff);
                System.out.printf("%-8s %10s %10s %12s%n", "attempts", "min", "max", "avg");
                for (int attempt = 0; attempt <= maxAttempts; attempt++) {
                    long lo = Long.MAX_VALUE;
                    long hi = Long.MIN_VALUE;
                    double sum = 0;
                    for (int s = 0; s < samples; s++) {
                        long v = backoff.backoff(attempt);
                        lo = Math.min(lo, v);
                        hi = Math.max(hi, v);
                        sum += v;
                    }
                    System.out.printf("%-8d %10d %10d %12.1f%n", attempt, lo, hi, sum / samples);
                }
            } catch (RuntimeException e) {
                System.out.println("[error] " + e);
            }
            System.out.println();
        }
    }
}
