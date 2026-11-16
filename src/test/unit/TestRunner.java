package test.unit;

import org.junit.platform.launcher.Launcher;
import org.junit.platform.launcher.LauncherDiscoveryRequest;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;
import org.junit.platform.launcher.listeners.TestExecutionSummary;

import static org.junit.platform.engine.discovery.DiscoverySelectors.selectClass;

public class TestRunner {
    public static void main(String[] args) {
        LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
                .selectors(selectClass(WalletDaoTest.class))
                .build();

        Launcher launcher = LauncherFactory.create();
        SummaryGeneratingListener listener = new SummaryGeneratingListener();
        launcher.registerTestExecutionListeners(listener);
        launcher.execute(request);

        TestExecutionSummary summary = listener.getSummary();
        System.out.println("============================================");
        System.out.println("KẾT QUẢ KIỂM THỬ ĐƠN VỊ (UNIT TEST - JUNIT)");
        System.out.println("============================================");
        System.out.println("Tổng số tests: " + summary.getTestsFoundCount());
        System.out.println("Thành công: " + summary.getTestsSucceededCount());
        System.out.println("Thất bại: " + summary.getTestsFailedCount());
        System.out.println("Bị bỏ qua: " + summary.getTestsSkippedCount());

        if (summary.getTestsFailedCount() > 0) {
            System.out.println("--- CHI TIẾT LỖI ---");
            summary.getFailures().forEach(failure -> {
                System.out.println("Test: " + failure.getTestIdentifier().getDisplayName());
                failure.getException().printStackTrace(System.out);
            });
            System.exit(1);
        } else {
            System.out.println(">>> TẤT CẢ UNIT TESTS ĐỀU PASS THÀNH CÔNG! <<<");
            System.exit(0);
        }
    }
}
