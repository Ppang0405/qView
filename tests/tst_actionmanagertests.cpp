#include <QtTest>

#include "qvapplication.h"
#include "qvimagecore.h"

class ActionManagerTests : public QObject
{
    Q_OBJECT

public:
    ActionManagerTests();
    ~ActionManagerTests();

private slots:
    void testClonedActionsUntracked();
    void testFolderNaturalSort();
};

ActionManagerTests::ActionManagerTests() { }

ActionManagerTests::~ActionManagerTests() { }

void ActionManagerTests::testClonedActionsUntracked()
{
    // Get initial counts of certain actions
    int fullscreenCount = qvApp->getActionManager().getAllInstancesOfAction("fullscreen").length();
    int openCount = qvApp->getActionManager().getAllInstancesOfAction("open").length();
    qDebug() << fullscreenCount;

    // Have window clone actions
    MainWindow window;
    window.show();
    // Make sure they were cloned
    QVERIFY(qvApp->getActionManager().getAllInstancesOfAction("fullscreen").length()
            != fullscreenCount);
    QVERIFY(qvApp->getActionManager().getAllInstancesOfAction("open").length() != openCount);
    // Untrack them
    window.close();

    // Make sure the count has not changed from the initial
    QCOMPARE(qvApp->getActionManager().getAllInstancesOfAction("fullscreen").length(),
             fullscreenCount);
    QCOMPARE(qvApp->getActionManager().getAllInstancesOfAction("open").length(), openCount);
}

void ActionManagerTests::testFolderNaturalSort()
{
    // Sorting runs in the Swift core; check it end to end through QVImageCore
    QTemporaryDir dir;
    QVERIFY(dir.isValid());
    for (const QString &name : { "img10.png", "img2.png", "img1.png" }) {
        QFile file(dir.filePath(name));
        QVERIFY(file.open(QIODevice::WriteOnly));
    }

    QVImageCore imageCore;
    imageCore.updateFolderInfo(dir.path());

    QStringList names;
    for (const auto &file : imageCore.getCurrentFileDetails().folderFileInfoList)
        names.append(file.fileName);
    QCOMPARE(names, QStringList({ "img1.png", "img2.png", "img10.png" }));
}

int main(int argc, char *argv[])
{
    QVApplication app(argc, argv);
    ActionManagerTests actionManagerTests;
    return QTest::qExec(&actionManagerTests, argc, argv);
}

#include "tst_actionmanagertests.moc"
