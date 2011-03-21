/********************************************************************************
** Form generated from reading UI file 'sumimagesr30564.ui'
**
** Created
**      by: Qt User Interface Compiler version 4.6.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef SUMIMAGESR30564_H
#define SUMIMAGESR30564_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QDialog>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QFrame>
#include <QtGui/QGridLayout>
#include <QtGui/QHBoxLayout>
#include <QtGui/QHeaderView>
#include <QtGui/QPushButton>
#include <QtGui/QTreeWidget>

QT_BEGIN_NAMESPACE

class Ui_FolienSummeDlg
{
public:
    QGridLayout *gridLayout;
    QTreeWidget *treeWidget;
    QDialogButtonBox *buttonBox;
    QFrame *frame;
    QHBoxLayout *horizontalLayout;
    QPushButton *pushButtonSelectAll;
    QPushButton *pushButtonSelectNone;
    QPushButton *pushButtonShow;

    void setupUi(QDialog *FolienSummeDlg)
    {
        if (FolienSummeDlg->objectName().isEmpty())
            FolienSummeDlg->setObjectName(QString::fromUtf8("FolienSummeDlg"));
        FolienSummeDlg->resize(274, 411);
        FolienSummeDlg->setMouseTracking(false);
        gridLayout = new QGridLayout(FolienSummeDlg);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        treeWidget = new QTreeWidget(FolienSummeDlg);
        treeWidget->setObjectName(QString::fromUtf8("treeWidget"));
        QSizePolicy sizePolicy(QSizePolicy::Minimum, QSizePolicy::Expanding);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(treeWidget->sizePolicy().hasHeightForWidth());
        treeWidget->setSizePolicy(sizePolicy);
        treeWidget->setMaximumSize(QSize(16777215, 16777215));
        treeWidget->header()->setVisible(false);
        treeWidget->header()->setCascadingSectionResizes(false);
        treeWidget->header()->setDefaultSectionSize(100);
        treeWidget->header()->setHighlightSections(false);
        treeWidget->header()->setProperty("showSortIndicator", QVariant(false));
        treeWidget->header()->setStretchLastSection(true);

        gridLayout->addWidget(treeWidget, 0, 0, 1, 1);

        buttonBox = new QDialogButtonBox(FolienSummeDlg);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Ok);

        gridLayout->addWidget(buttonBox, 5, 0, 1, 1);

        frame = new QFrame(FolienSummeDlg);
        frame->setObjectName(QString::fromUtf8("frame"));
        frame->setFrameShape(QFrame::StyledPanel);
        frame->setFrameShadow(QFrame::Plain);
        horizontalLayout = new QHBoxLayout(frame);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        pushButtonSelectAll = new QPushButton(frame);
        pushButtonSelectAll->setObjectName(QString::fromUtf8("pushButtonSelectAll"));

        horizontalLayout->addWidget(pushButtonSelectAll);

        pushButtonSelectNone = new QPushButton(frame);
        pushButtonSelectNone->setObjectName(QString::fromUtf8("pushButtonSelectNone"));

        horizontalLayout->addWidget(pushButtonSelectNone);


        gridLayout->addWidget(frame, 3, 0, 1, 1);

        pushButtonShow = new QPushButton(FolienSummeDlg);
        pushButtonShow->setObjectName(QString::fromUtf8("pushButtonShow"));

        gridLayout->addWidget(pushButtonShow, 4, 0, 1, 1);


        retranslateUi(FolienSummeDlg);
        QObject::connect(buttonBox, SIGNAL(accepted()), FolienSummeDlg, SLOT(accept()));
        QObject::connect(buttonBox, SIGNAL(rejected()), FolienSummeDlg, SLOT(reject()));

        QMetaObject::connectSlotsByName(FolienSummeDlg);
    } // setupUi

    void retranslateUi(QDialog *FolienSummeDlg)
    {
        FolienSummeDlg->setWindowTitle(QApplication::translate("FolienSummeDlg", "Sum Images", 0, QApplication::UnicodeUTF8));
        QTreeWidgetItem *___qtreewidgetitem = treeWidget->headerItem();
        ___qtreewidgetitem->setText(0, QApplication::translate("FolienSummeDlg", "Auswahl", 0, QApplication::UnicodeUTF8));
        pushButtonSelectAll->setText(QApplication::translate("FolienSummeDlg", "Select All", 0, QApplication::UnicodeUTF8));
        pushButtonSelectNone->setText(QApplication::translate("FolienSummeDlg", "Select None", 0, QApplication::UnicodeUTF8));
        pushButtonShow->setText(QApplication::translate("FolienSummeDlg", "Show", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class FolienSummeDlg: public Ui_FolienSummeDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // SUMIMAGESR30564_H
