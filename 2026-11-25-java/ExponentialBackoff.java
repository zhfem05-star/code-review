package org.apache.kafka.common.utils.internals;

import java.util.concurrent.ThreadLocalRandom;

import static java.lang.String.format;

/**
 * A utility class for keeping the parameters and providing the value of exponential
 * retry backoff, exponential reconnect backoff, exponential timeout, etc.
 * <p>
 * The formula is:
 * <pre>Backoff(attempts) = random(1 - jitter, 1 + jitter) * initialInterval * multiplier ^ attempts</pre>
 * If {$code maxInterval} is less that {@code initialInterval}, a constant backoff of
 * {@code maxInterval} will be provided. The jitter will never cause the backoff to exceed
 * {@code maxInterval}.
 * <p>
 * This class is thread-safe.
 */
public class ExponentialBackoff {
    private final long initialInterval;
    private final int multiplier;
    private final long maxInterval;
    private final double jitter;
    private final double expMax;

    public ExponentialBackoff(long initialInterval, int multiplier, long maxInterval, double jitter) {
        this.initialInterval = Math.min(maxInterval, initialInterval);
        this.multiplier = multiplier;
        this.maxInterval = maxInterval;
        if (jitter < 0 || jitter > 1) {
            throw new IllegalArgumentException(format("jitter must be between 0 and 1, but got %s", jitter));
        }
        this.jitter = jitter;
        this.expMax = maxInterval > initialInterval ?
                Math.log(maxInterval / (double) Math.max(initialInterval, 1)) / Math.log(multiplier) : 0;
    }

    public long initialInterval() {
        return initialInterval;
    }

    public long backoff(long attempts) {
        if (expMax == 0) {
            return initialInterval;
        }
        double exp = Math.min(attempts, this.expMax);
        double term = initialInterval * Math.pow(multiplier, exp);
        double randomFactor = jitter < Double.MIN_NORMAL ? 1.0 :
            ThreadLocalRandom.current().nextDouble(1 - jitter, 1 + jitter);
        long backoffValue = (long) (randomFactor * term);
        return Math.min(backoffValue, maxInterval);
    }

    @Override
    public String toString() {
        return "ExponentialBackoff{" +
                "multiplier=" + multiplier +
                ", expMax=" + expMax +
                ", initialInterval=" + initialInterval +
                ", jitter=" + jitter +
                '}';
    }
}
