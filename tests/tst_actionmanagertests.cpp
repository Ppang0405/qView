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
    void testFolderSortIsLocaleAware();
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
    // Sorting runs in the Swift core; check it end to end through QVImageCore.
    // Collation in the C locale is plain byte order, so pin a real locale.
    QLocale::setDefault(QLocale(QLocale::English, QLocale::UnitedStates));
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

void ActionManagerTests::testFolderSortIsLocaleAware()
{
    // Accented names must sort with their base letter, as QCollator does
    QLocale::setDefault(QLocale(QLocale::English, QLocale::UnitedStates));
    QTemporaryDir dir;
    QVERIFY(dir.isValid());
    for (const QString &name :
         QStringList({ "zebra.png", QString::fromUtf8("éclair.png"), "apple.png" })) {
        QFile file(dir.filePath(name));
        QVERIFY(file.open(QIODevice::WriteOnly));
    }

    QVImageCore imageCore;
    imageCore.updateFolderInfo(dir.path());

    QStringList names;
    for (const auto &file : imageCore.getCurrentFileDetails().folderFileInfoList)
        names.append(file.fileName);
    QCOMPARE(names, QStringList({ "apple.png", QString::fromUtf8("éclair.png"), "zebra.png" }));
}

int main(int argc, char *argv[])
{
    QVApplication app(argc, argv);
    ActionManagerTests actionManagerTests;
    return QTest::qExec(&actionManagerTests, argc, argv);
}

#include "tst_actionmanagertests.moc"
